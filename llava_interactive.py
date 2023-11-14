import argparse
import base64
import io
import os
import sys

import cv2
import gradio as gr
import numpy as np
import requests
from functools import partial
from PIL import Image, ImageOps

sys.path.append(os.path.join(os.environ['LLAVA_INTERACTIVE_HOME'], 'GLIGEN/demo'))
import GLIGEN.demo.app as GLIGEN

sys.path.append(os.path.join(os.environ['LLAVA_INTERACTIVE_HOME'], 'SEEM/demo_code'))
import SEEM.demo_code.app as SEEM  # must import GLIGEN_app before this. Otherwise, it will hit a protobuf error

sys.path.append(os.path.join(os.environ['LLAVA_INTERACTIVE_HOME'], 'LLaVA'))
import LLaVA.llava.serve.gradio_web_server as LLAVA


class ImageMask(gr.components.Image):
    """
    Sets: source="canvas", tool="sketch"
    """

    is_template = True

    def __init__(self, **kwargs):
        super().__init__(source="upload", tool="sketch", interactive=True, **kwargs)

    def preprocess(self, x):
        if isinstance(x, str):
            x = {'image': x, 'mask': x}
        elif isinstance(x, dict):
            if x['mask'] is None and x['image'] is None:
                x
            elif x['image'] is None:
                x['image'] = str(x['mask'])
            elif x['mask'] is None:
                x['mask'] = str(
                    x['image']
                )  # not sure why mask/mask is None sometimes, this prevents preprocess crashing
        elif x is not None:
            assert False, 'Unexpected type {0} in ImageMask preprocess()'.format(type(x))

        return super().preprocess(x)


css = """
#compose_btn {
    --tw-border-opacity: 1;
    border-color: rgb(255 216 180 / var(--tw-border-opacity));
    --tw-gradient-from: rgb(255 216 180 / .7);
    --tw-gradient-to: rgb(255 216 180 / 0);
    --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
    --tw-gradient-to: rgb(255 176 102 / .8);
    --tw-text-opacity: 1;
    color: rgb(238 116 0 / var(--tw-text-opacity));
}
"""


def get_bounding_box(img):
    # Get the indices of all non-zero pixels
    if np.any(img) == False:  # protect agaist an empty img
        return None
    non_zero_indices = np.nonzero(img)

    # Get the minimum and maximum indices for each axis
    min_x = np.min(non_zero_indices[1])
    max_x = np.max(non_zero_indices[1])
    min_y = np.min(non_zero_indices[0])
    max_y = np.max(non_zero_indices[0])

    # Return the bounding box as a tuple of (min_x, min_y, max_x, max_y)
    return (min_x, min_y, max_x, max_y)


def composite_all_layers(base, objects):  # debugging use only
    img = base.copy()
    for obj in objects:
        for i in range(obj['img'].shape[0]):
            for j in range(obj['img'].shape[1]):
                if obj['img'][i, j, 3] != 0:
                    img[i, j] = obj['img'][i, j]
    return img


def changed_objects_handler(mask_dilate_slider, state, evt: gr.SelectData):
    state['move_no'] += 1

    pos_x, pos_y = evt.index  # obj moved out of scene is signaled by (10000, 10000)
    obj_id = 255 - evt.value
    print(f"obj {obj_id} moved by {pos_x}, {pos_y}")

    img = state['base_layer']
    for obj in state['changed_objects']:
        if obj['id'] == obj_id:
            img = obj['img']
            state['changed_objects'].remove(obj)
            break

    new_img = np.zeros_like(img)
    bbox = None
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 3] == obj_id:
                new_i = i + pos_y
                new_j = j + pos_x
                if new_i >= 0 and new_i < img.shape[0] and new_j >= 0 and new_j < img.shape[1]:
                    new_img[new_i, new_j] = img[i, j]
                img[i, j] = 0

    bbox = get_bounding_box(new_img)  # returns None if obj moved out of scene
    print("bbox: ", bbox)
    state['changed_objects'].append({'id': obj_id, 'img': new_img, 'text': state['segment_info'][obj_id], 'box': bbox})

    # Enable for debugging only. See if the composited image is correct.
    # composed_img_updated = composite_all_layers(state['base_layer'], state['changed_objects'])
    # filename = str(f"composited_imge_{state['move_no']}") + ".png"
    # cv2.imwrite(filename, composed_img_updated[:, :, 0:3])

    return mask_dilate_slider, state['base_layer_masked'], state


def get_base_layer_mask(state):
    changed_obj_id = []
    for obj in state['changed_objects']:
        changed_obj_id.append(obj['id'])

    # union of mask of all objects
    img = state['orignal_segmented']
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i, j, 3] in changed_obj_id:
                mask[i, j] = 255
    state['base_layer_mask'] = mask

    mask_image = Image.fromarray(mask)
    if mask_image.mode != "L":
        mask_image = mask_image.convert("L")
    mask_image = ImageOps.invert(mask_image)
    # mask_image.save("mask_image.png")

    img = state['orignal_segmented']
    orig_image = Image.fromarray(img[:, :, :3])
    orig_image.save("orig_image.png")
    transparent = Image.new(orig_image.mode, orig_image.size, (0, 0, 0, 0))
    masked_image = Image.composite(orig_image, transparent, mask_image)
    # masked_image.save("get_masked_background_image.png")

    return masked_image, state


def get_inpainted_background(state, mask_dilate_slider):
    # Define the URL of the REST API endpoint
    url = "http://localhost:9171/api/v2/image"

    img = state['orignal_segmented']
    if isinstance(img, Image.Image) is not True:
        img = Image.fromarray(img)
    # Create a BytesIO object and save the image there
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    # Get the bytes value from the buffer
    img_bytes = buffer.getvalue()

    encoded_string = base64.b64encode(img_bytes).decode("utf-8")

    if mask_dilate_slider != 0:
        mask = state['base_layer_mask_enlarged']
    else:
        mask = state['base_layer_mask']
    if isinstance(mask, Image.Image) is not True:
        mask = Image.fromarray(mask)

    # mask has background as 1, lama needs object to be 1
    if mask.mode != "L":
        mask = mask.convert("L")
    mask = ImageOps.invert(mask)

    # Create a BytesIO object and save the image there
    buffer = io.BytesIO()
    mask.save(buffer, format="PNG")
    # Get the bytes value from the buffer
    mask_bytes = buffer.getvalue()

    encoded_string_mask = base64.b64encode(mask_bytes).decode("utf-8")

    # Create a POST request to the endpoint
    headers = {"Content-Type": "application/json"}
    data = {"image": encoded_string, "mask": encoded_string_mask}
    response = requests.post(url, headers=headers, json=data)

    # Check the status code of the response
    if response.status_code == 200:
        # The request was successful
        print("Image received successfully")
        image_data = response.content
        # Create a io.BytesIO object from the image data
        dataBytesIO = io.BytesIO(image_data)
        # Open the image using Image.open()
        image = Image.open(dataBytesIO)
        # image.save("lama_returned_image.png")

    else:
        # The request failed
        print("Error: HTTP status code {}".format(response.status_code))
        print(response.text)

    return image


def get_enlarged_masked_background(state, mask_dilate_slider):
    mask = state['base_layer_mask']

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (mask_dilate_slider, mask_dilate_slider))
    mask_dilated = cv2.dilate(mask, kernel)

    # mask the original
    mask_image = Image.fromarray(mask_dilated)
    if mask_image.mode != "L":
        mask_image = mask_image.convert("L")
    mask_image = ImageOps.invert(mask_image)
    state['base_layer_mask_enlarged'] = mask_image
    # mask_image.save("enlarged_mask_image.png")

    img = state['orignal_segmented']
    orig_image = Image.fromarray(img[:, :, :3])
    transparent = Image.new(orig_image.mode, orig_image.size, (0, 0, 0, 0))
    masked_image = Image.composite(orig_image, transparent, mask_image)
    # masked_image.save("enlarged_masked_background_image.png")

    return masked_image, state


def get_base_layer_inpainted(state, mask_dilate_slider):
    masked_img, state = get_enlarged_masked_background(state, mask_dilate_slider)
    inpainted_img = get_inpainted_background(state, mask_dilate_slider)
    state['base_layer_inpainted'] = np.array(inpainted_img)
    return masked_img, inpainted_img, state


def log_image_and_mask(img, mask):  # for debugging use only
    counter = 0
    for filename in os.listdir('.'):
        if filename.startswith('img_') and filename.endswith('.png'):
            try:
                num = int(filename[4:-4])
                if num > counter:
                    counter = num
            except ValueError:
                pass
    counter += 1
    cv2.imwrite(f"img_{counter}.png", img)
    cv2.imwrite(f"img_{counter}_mask.png", mask.astype(np.uint8) * 255)


def get_segments(img, task, reftxt, mask_dilate_slider, state):
    assert isinstance(state, dict)
    state['orignal_segmented'] = None
    state['base_layer'] = None
    state['base_layer_masked'] = None
    state['base_layer_mask'] = None
    state['base_layer_mask_enlarged'] = None
    state['base_layer_inpainted'] = None
    state['segment_info'] = None
    state['seg_boxes'] = {}
    state['changed_objects'] = []
    state['move_no'] = 0

    print("Calling SEEM_app.inference")

    if isinstance(img['image'], np.ndarray):
        pil_image = Image.fromarray(img['image'])
    if isinstance(img['mask'], np.ndarray):
        pil_mask = Image.fromarray(img['mask'])
    img = {'image': pil_image, 'mask': pil_mask}
    img_ret, seg_info = SEEM.inference(img, task, reftxt=reftxt)
    # SEEM doesn't always respect the input img dimentions
    tgt_size = (img['image'].width, img['image'].height)
    img_ret = img_ret.resize(tgt_size, resample=Image.Resampling.NEAREST)
    state['orignal_segmented'] = np.array(img_ret).copy()
    state['base_layer'] = np.array(img_ret)
    state['segment_info'] = seg_info
    img_ret_array = np.array(img_ret)
    img_ret_array[:, :, 3] = 255 - img_ret_array[:, :, 3]
    # NOTE: if write out as a png, the pixels values get messed up. Same reason the client side colors look weird.
    # cv2.imwrite(f"get_segments_img_ret.bmp", img_ret_array)

    for obj_id, lable in seg_info.items():
        obj_img = img_ret_array[:, :, 3] == 255 - obj_id
        # cv2.imwrite(f"img_{obj_id}.png", obj_img.astype(np.uint8) * 255)
        # log_image_and_mask(np.array(img['image']), obj_img)
        bbox = get_bounding_box(obj_img)
        print(f"obj_id={obj_id}, lable={lable}, bbox={bbox}")
        state['seg_boxes'][obj_id] = bbox

    # add a special event, obj stays at the original spot
    data = {}
    data["index"] = (0, 0)
    data["value"] = 254  # ==> 1, the only object allowed for now
    data["selected"] = True
    evt = gr.SelectData(None, data)
    mask_dilate_slider, _, state = changed_objects_handler(mask_dilate_slider, state, evt)

    state['base_layer_masked'], state = get_base_layer_mask(state)
    if mask_dilate_slider != 0:
        enlarged_masked_background, state = get_enlarged_masked_background(state, mask_dilate_slider)
    state['base_layer_inpainted'] = np.array(get_inpainted_background(state, mask_dilate_slider))

    return Image.fromarray(img_ret_array), enlarged_masked_background, state['base_layer_inpainted'], state


def get_generated(grounding_text, fix_seed, rand_seed, state):
    if ('base_layer_inpainted' in state) == False:
        raise gr.Error('The segmentation step must be completed first before generating a new image')

    inpainted_background_img = state['base_layer_inpainted']
    assert inpainted_background_img is not None, 'base layer should be inpainted after segment'

    state['boxes'] = []
    for items in state['changed_objects']:
        if items['box'] is not None:
            state['boxes'].append(items['box'])

    if len(state['boxes']) == 0:
        if len(grounding_text) != 0:
            grounding_text = []
            print("No grounding box found. Grounding text will be ignored.")
        return inpainted_background_img.copy(), state, None

    print('Calling GLIGEN_app.generate')
    print('grounding_text: ', grounding_text)
    print(state['boxes'], len(state['boxes']))
    assert len(state['boxes']) == 1, 'Only handle one segmented object at a time'
    if len(grounding_text) == 0:  # mostly user forgot to drag the object and didn't provide grounding text
        raise gr.Error('Please providing grounding text to match the identified object')
    out_gen_1, _, _, _, state = GLIGEN.generate(
        task='Grounded Inpainting',
        language_instruction='',
        grounding_texts=grounding_text,
        sketch_pad=inpainted_background_img,
        alpha_sample=0.3,
        guidance_scale=7.5,
        batch_size=1,
        fix_seed=fix_seed,
        rand_seed=rand_seed,
        use_actual_mask=False,
        append_grounding=True,
        style_cond_image=None,
        inpainting_image=inpainted_background_img,
        inpainting_mask=None,
        state=state,
    )

    return out_gen_1['value'], state


def get_generated_full(
    task,
    language_instruction,
    grounding_instruction,
    sketch_pad,
    alpha_sample,
    guidance_scale,
    batch_size,
    fix_seed,
    rand_seed,
    use_actual_mask,
    append_grounding,
    style_cond_image,
    state,
):
    out_gen_1, _, _, _, state = GLIGEN.generate(
        task,
        language_instruction,
        grounding_instruction,
        sketch_pad,
        alpha_sample,
        guidance_scale,
        batch_size,
        fix_seed,
        rand_seed,
        use_actual_mask,
        append_grounding,
        style_cond_image,
        state,
    )
    return out_gen_1['value'], state


def gligen_change_task(state):
    if state['working_image'] is not None:
        task = "Grounded Inpainting"
    else:
        task = "Grounded Generation"
    return task


def clear_sketch_pad_mask(sketch_pad_image):
    sketch_pad = ImageMask.update(value=sketch_pad_image, visible=True)
    return sketch_pad


def save_shared_state(img, state):
    if isinstance(img, dict) and 'image' in img:
        state['working_image'] = img['image']
    else:
        state['working_image'] = img
    return state


def load_shared_state(state, task=None):
    if task == "Grounded Generation":
        return None
    else:
        return state['working_image']


def update_shared_state(state, task):
    if task == "Grounded Generation":
        state['working_image'] = None
    return state


def update_sketch_pad_trigger(sketch_pad_trigger, task):
    if task == "Grounded Generation":
        sketch_pad_trigger = sketch_pad_trigger + 1
    return sketch_pad_trigger


def clear_grounding_info(state):
    state['boxes'] = []
    state['masks'] = []
    return state, ''


def switch_to_generate():
    task = "Grounded Generation"
    return (
        task,
        gr.Image.update(visible=True),
        gr.Textbox.update(visible=True),
        gr.Textbox.update(visible=True),
        gr.Button.update(visible=True),
        gr.Button.update(visible=True),
        gr.Accordion.update(visible=True),
    )


def switch_to_inpaint():
    task = "Grounded Inpainting"
    return (
        task,
        gr.Image.update(visible=True),
        gr.Textbox.update(visible=False),
        gr.Textbox.update(visible=True),
        gr.Button.update(visible=True),
        gr.Button.update(visible=True),
        gr.Accordion.update(visible=True),
    )


def switch_to_compose():
    task = "Compose"
    return (
        task,
        gr.Image.update(visible=False),
        gr.Textbox.update(visible=False),
        gr.Textbox.update(visible=False),
        gr.Button.update(visible=False),
        gr.Button.update(visible=False),
        gr.Accordion.update(visible=False),
    )


def copy_to_llava_input(img):
    print('WORKING IMAGE CHANGED!!!!')
    if isinstance(img, Image.Image) is not True:
        img = Image.fromarray(img)
    return img


def build_demo():
    demo = gr.Blocks(title="🌋 LLaVA-Interactive", css=css + GLIGEN.css)
    with demo:
        compose_state = gr.State(
            {
                'boxes': [],
                'move_no': 0,
                'base_layer': None,
                'segment_info': None,
                'seg_boxes': {},
                'changed_objects': [],
            }
        )
        llava_state = gr.State()
        shared_state = gr.State({'working_image': None})
        gligen_state = gr.State({'draw_box': True})

        gr.HTML('<h1 style="text-align: center;"></h1>')
        gr.HTML('<h1 style="text-align: center;">LLaVA Interactive</h1>')
        gr.HTML('<h1 style="text-align: center;"></h1>')

        gr.Markdown(
            '**Experience interactive multimodal chatting and image manipulation. Select a tab for your task and follow the instructions. Switch tasks anytime and ask questions in the chat window.**'
        )

        with gr.Row(visible=False):
            working_image = gr.Image(
                label="Working Image", type="numpy", elem_id="working_image", visible=False, interactive=False
            )  # hidden image to save current working image
            # for gligen
            sketch_pad_trigger = gr.Number(value=0, visible=False)
            sketch_pad_resize_trigger = gr.Number(value=0, visible=False)
            init_white_trigger = gr.Number(value=0, visible=False)
            image_scale = gr.Number(value=0, elem_id="image_scale", visible=False)
            task = gr.Radio(
                choices=["Grounded Generation", 'Grounded Inpainting', 'Compose'],
                type="value",
                value="Grounded Inpainting",
                label="Task",
                visible=False,
            )

        with gr.Row(equal_height=False):
            with gr.Column():
                with gr.Row():
                    sketch_pad = ImageMask(
                        label="Sketch Pad",
                        type="numpy",
                        shape=(512, 512),
                        width=384,
                        elem_id="img2img_image",
                        brush_radius=20.0,
                        visible=True,
                    )

                compose_tab = gr.Tab("Remove or Change Objects")
                with compose_tab:
                    gr.Markdown(
                        "Segment an object by drawing a stroke or giving a referring text. Then press the segment button. Drag the highlighted object to move it. To remove it, drag it out of the frame. To replace it with a new object, give an instruction only if the object is removed and press the generate button until you like the image."
                    )
                    with gr.Row().style(equal_height=False):
                        with gr.Column():
                            with gr.Group():
                                with gr.Column():
                                    with gr.Row():
                                        segment_task = gr.Radio(
                                            ["Stroke", "Text"], value="Stroke", label='Choose segmentation method'
                                        )
                                        segment_text = gr.Textbox(label="Enter referring text")
                                    segment_btn = gr.Button("Segment", elem_id="segment-btn")

                            with gr.Group():
                                segmented_img = gr.Image(label="Move or delete object", tool="compose", height=256)

                            with gr.Group():
                                with gr.Column():
                                    grounding_text_box = gr.Textbox(
                                        label="Enter grounding text for generating a new image"
                                    )
                                    with gr.Row():
                                        compose_clear_btn = gr.Button("Clear", elem_id="compose_clear_btn")
                                        compose_btn = gr.Button("Generate", elem_id="compose_btn")

                            with gr.Accordion("Advanced Options", open=False):
                                with gr.Row():
                                    masked_background_img = gr.Image(
                                        label="Background", type='pil', interactive=False, height=256
                                    )
                                    inpainted_background_img = gr.Image(
                                        label="Inpainted Background", type='pil', interactive=False, height=256
                                    )
                                mask_dilate_slider = gr.Slider(
                                    minimum=0.0,
                                    maximum=100,
                                    value=50,
                                    step=2,
                                    interactive=True,
                                    label="Mask dilation",
                                    visible=True,
                                    scale=20,
                                )
                                with gr.Row(visible=False):
                                    compose_fix_seed = gr.Checkbox(value=False, label="Fixed seed", visible=False)
                                    compose_rand_seed = gr.Slider(
                                        minimum=0, maximum=1000, step=1, value=0, label="Seed", visible=False
                                    )

                gligen_inpaint = gr.Tab("Inpaint New Objects")
                with gligen_inpaint:
                    gr.Markdown(
                        "Add a new object to the image by drawing its bounding box and giving an instruction. Press the “generate” button repeatedly until you like the image. Press “clear” to accept the image and start over with another object."
                    )

                gligen = gr.Tab("Generate New Image")
                with gligen:
                    gr.Markdown(
                        "Generate a new image by giving a language instruction below. Draw a bounding box and give an instruction for any specific objects that need to be grounded in certain places. Hit the “generate” button repeatedly until you get the image you want."
                    )

                with gr.Group(visible=False):
                    language_instruction = gr.Textbox(
                        label="Language instruction", elem_id='language_instruction', visible=False
                    )
                    grounding_instruction = gr.Textbox(
                        label="Grounding instruction (Separated by semicolon)",
                        elem_id='grounding_instruction',
                        visible=False,
                    )
                    with gr.Row():
                        gligen_clear_btn = gr.Button(value='Clear', visible=False)
                        gligen_gen_btn = gr.Button(value='Generate', elem_id="generate-btn", visible=False)

                with gr.Group():
                    out_imagebox = gr.Image(type="pil", label="Parsed Sketch Pad", height=256, visible=False)

                gligen_adv_options = gr.Accordion("Advanced Options", open=False, visible=False)
                with gligen_adv_options:
                    with gr.Column():
                        alpha_sample = gr.Slider(
                            minimum=0, maximum=1.0, step=0.1, value=0.3, label="Scheduled Sampling (τ)"
                        )
                        guidance_scale = gr.Slider(minimum=0, maximum=50, step=0.5, value=7.5, label="Guidance Scale")

                with gr.Row(visible=False):
                    batch_size = gr.Slider(
                        minimum=1, maximum=4, step=1, value=1, label="Number of Samples", visible=False
                    )
                    append_grounding = gr.Checkbox(
                        value=True, label="Append grounding instructions to the caption", visible=False
                    )
                    use_actual_mask = gr.Checkbox(value=False, label="Use actual mask for inpainting", visible=False)
                    fix_seed = gr.Checkbox(value=False, label="Fixed seed", visible=False)
                    rand_seed = gr.Slider(minimum=0, maximum=1000, step=1, value=0, label="Seed", visible=False)
                    use_style_cond = gr.Checkbox(value=False, label="Enable Style Condition", visible=False)
                    style_cond_image = gr.Image(type="pil", label="Style Condition", visible=False, interactive=False)

                controller = GLIGEN.Controller()
                sketch_pad.edit(
                    GLIGEN.draw,
                    inputs=[task, sketch_pad, grounding_instruction, sketch_pad_resize_trigger, gligen_state],
                    outputs=[out_imagebox, sketch_pad_resize_trigger, image_scale, gligen_state],
                    queue=False,
                )
                llava_image = gr.Image(label='sketch_pad_image', type='pil', visible=False, interactive=False)
                working_image.change(copy_to_llava_input, [working_image], [llava_image])
                sketch_pad.upload(save_shared_state, inputs=[sketch_pad, shared_state], outputs=shared_state).then(
                    load_shared_state, [shared_state], working_image
                )
                grounding_instruction.change(
                    GLIGEN.draw,
                    inputs=[task, sketch_pad, grounding_instruction, sketch_pad_resize_trigger, gligen_state],
                    outputs=[out_imagebox, sketch_pad_resize_trigger, image_scale, gligen_state],
                    queue=False,
                )
                gligen_clear_btn.click(
                    GLIGEN.clear,
                    inputs=[task, sketch_pad_trigger, batch_size, gligen_state],
                    outputs=[sketch_pad, sketch_pad_trigger, out_imagebox, image_scale, gligen_state],
                    queue=False,
                ).then(clear_grounding_info, gligen_state, [gligen_state, grounding_instruction]).then(
                    load_shared_state, [shared_state], sketch_pad
                ).then(
                    update_sketch_pad_trigger, [sketch_pad_trigger, task], sketch_pad_trigger
                )
                task.change(
                    partial(GLIGEN.clear, switch_task=True),
                    inputs=[task, sketch_pad_trigger, batch_size, gligen_state],
                    outputs=[sketch_pad, sketch_pad_trigger, out_imagebox, image_scale, gligen_state],
                    queue=False,
                ).then(load_shared_state, [shared_state, task], sketch_pad).then(
                    update_sketch_pad_trigger, [sketch_pad_trigger, task], sketch_pad_trigger
                ).then(
                    clear_grounding_info, gligen_state, [gligen_state, grounding_instruction]
                )
                sketch_pad_trigger.change(
                    controller.init_white,
                    inputs=[init_white_trigger],
                    outputs=[sketch_pad, image_scale, init_white_trigger],
                    queue=False,
                )
                sketch_pad_resize_trigger.change(
                    controller.resize_masked, inputs=[gligen_state], outputs=[sketch_pad, gligen_state], queue=False
                )

                gligen_gen_btn.click(
                    get_generated_full,
                    inputs=[
                        task,
                        language_instruction,
                        grounding_instruction,
                        sketch_pad,
                        alpha_sample,
                        guidance_scale,
                        batch_size,
                        fix_seed,
                        rand_seed,
                        use_actual_mask,
                        append_grounding,
                        style_cond_image,
                        gligen_state,
                    ],
                    outputs=[sketch_pad, gligen_state],
                    queue=True,
                ).then(save_shared_state, [sketch_pad, shared_state], shared_state).then(
                    load_shared_state, [shared_state], working_image
                )

                sketch_pad_resize_trigger.change(
                    None, None, sketch_pad_resize_trigger, _js=GLIGEN.rescale_js, queue=False
                )
                init_white_trigger.change(None, None, init_white_trigger, _js=GLIGEN.rescale_js, queue=False)
                use_style_cond.change(
                    lambda cond: gr.Image.update(visible=cond), use_style_cond, style_cond_image, queue=False
                )
                task.change(
                    controller.switch_task_hide_cond,
                    inputs=task,
                    outputs=[use_style_cond, style_cond_image, alpha_sample, use_actual_mask],
                    queue=False,
                )

            with gr.Column():
                llava_chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    label="Chat with the latest image on the left at any time by entering your text below.",
                    height=750,
                )
                with gr.Column(scale=8):
                    llava_textbox = gr.Textbox(
                        show_label=False, placeholder="Enter text and press ENTER", container=False
                    )
                with gr.Column(scale=1, min_width=60):
                    llava_submit_btn = gr.Button(value="Submit", visible=False)

                with gr.Row(visible=False):
                    upvote_btn = gr.Button(value="👍  Upvote", interactive=False, visible=False)
                    downvote_btn = gr.Button(value="👎  Downvote", interactive=False, visible=False)
                    flag_btn = gr.Button(value="⚠️  Flag", interactive=False, visible=False)
                    regenerate_btn = gr.Button(value="🔄  Regenerate", interactive=False, visible=False)
                    llava_clear_btn = gr.Button(value="🗑️  Clear history", interactive=False, visible=False)
                    with gr.Accordion("Parameters", open=False, visible=False) as parameter_row:
                        temperature = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.2,
                            step=0.1,
                            interactive=True,
                            label="Temperature",
                            visible=True,
                        )
                        top_p = gr.Slider(
                            minimum=0.0, maximum=1.0, value=0.7, step=0.1, interactive=True, label="Top P", visible=True
                        )
                        max_output_tokens = gr.Slider(
                            minimum=0,
                            maximum=1024,
                            value=512,
                            step=64,
                            interactive=True,
                            label="Max output tokens",
                            visible=True,
                        )

        segment_btn.click(
            get_segments,
            inputs=[sketch_pad, segment_task, segment_text, mask_dilate_slider, compose_state],
            outputs=[segmented_img, masked_background_img, inpainted_background_img, compose_state],
            queue=True,
        )
        segmented_img.select(
            changed_objects_handler,
            [mask_dilate_slider, compose_state],
            [mask_dilate_slider, masked_background_img, compose_state],
        )
        mask_dilate_slider.release(
            get_base_layer_inpainted,
            inputs=[compose_state, mask_dilate_slider],
            outputs=[masked_background_img, inpainted_background_img, compose_state],
        )
        compose_btn.click(
            get_generated,
            [grounding_text_box, compose_fix_seed, compose_rand_seed, compose_state],
            [sketch_pad, compose_state],
            queue=True,
        ).then(save_shared_state, [sketch_pad, shared_state], shared_state).then(
            load_shared_state, [shared_state], working_image
        )
        compose_clear_btn.click(load_shared_state, [shared_state], sketch_pad)

        image_process_mode = gr.Radio(
            ["Crop", "Resize", "Pad"], value="Crop", label="Preprocess for non-square image", visible=False
        )
        models = LLAVA.get_model_list(args)
        model_selector = gr.Dropdown(
            choices=models,
            value=models[0] if len(models) > 0 else "",
            interactive=True,
            show_label=False,
            container=False,
            visible=False,
        )

        btn_list = [upvote_btn, downvote_btn, flag_btn, regenerate_btn, llava_clear_btn]
        upvote_btn.click(
            LLAVA.upvote_last_response,
            [llava_state, model_selector],
            [llava_textbox, upvote_btn, downvote_btn, flag_btn],
        )
        downvote_btn.click(
            LLAVA.downvote_last_response,
            [llava_state, model_selector],
            [llava_textbox, upvote_btn, downvote_btn, flag_btn],
        )
        flag_btn.click(
            LLAVA.flag_last_response, [llava_state, model_selector], [llava_textbox, upvote_btn, downvote_btn, flag_btn]
        )
        regenerate_btn.click(
            LLAVA.regenerate,
            [llava_state, image_process_mode],
            [llava_state, llava_chatbot, llava_textbox, sketch_pad] + btn_list,
        ).then(
            LLAVA.http_bot,
            [llava_state, model_selector, temperature, top_p, max_output_tokens],
            [llava_state, llava_chatbot] + btn_list,
        )
        llava_clear_btn.click(
            LLAVA.clear_history, None, [llava_state, llava_chatbot, llava_textbox, llava_image] + btn_list
        )

        llava_textbox.submit(
            LLAVA.add_text,
            [llava_state, llava_textbox, llava_image, image_process_mode],
            [llava_state, llava_chatbot, llava_textbox, llava_image] + btn_list,
        ).then(
            LLAVA.http_bot,
            [llava_state, model_selector, temperature, top_p, max_output_tokens],
            [llava_state, llava_chatbot] + btn_list,
        )
        llava_submit_btn.click(
            LLAVA.add_text,
            [llava_state, llava_textbox, llava_image, image_process_mode],
            [llava_state, llava_chatbot, llava_textbox, llava_image] + btn_list,
        ).then(
            LLAVA.http_bot,
            [llava_state, model_selector, temperature, top_p, max_output_tokens],
            [llava_state, llava_chatbot] + btn_list,
        )

        if args.model_list_mode == "once":
            raise ValueError(f"Unsupported model list mode: {args.model_list_mode}")
        elif args.model_list_mode == "reload":
            print('disable for debugging')
            demo.load(LLAVA.load_demo_refresh_model_list, inputs=None, outputs=[llava_state, model_selector]).then(
                switch_to_compose,
                [],
                [
                    task,
                    out_imagebox,
                    language_instruction,
                    grounding_instruction,
                    gligen_clear_btn,
                    gligen_gen_btn,
                    gligen_adv_options,
                ],  # first tab show doesn't need any
            ).then(
                GLIGEN.clear,
                inputs=[task, sketch_pad_trigger, batch_size, gligen_state],
                outputs=[sketch_pad, sketch_pad_trigger, out_imagebox, image_scale, gligen_state],
                queue=False,
            )

        else:
            raise ValueError(f"Unknown model list mode: {args.model_list_mode}")

        gligen.select(
            switch_to_generate,
            inputs=[],
            outputs=[
                task,
                out_imagebox,
                language_instruction,
                grounding_instruction,
                gligen_clear_btn,
                gligen_gen_btn,
                gligen_adv_options,
            ],
        )
        gligen_inpaint.select(
            switch_to_inpaint,
            inputs=[],
            outputs=[
                task,
                out_imagebox,
                language_instruction,
                grounding_instruction,
                gligen_clear_btn,
                gligen_gen_btn,
                gligen_adv_options,
            ],
            queue=False,
        )

        compose_tab.select(
            switch_to_compose,
            [],
            [
                task,
                out_imagebox,
                language_instruction,
                grounding_instruction,
                gligen_clear_btn,
                gligen_gen_btn,
                gligen_adv_options,
            ],
        )

    return demo


class LowercaseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        lowercase_values = [v.lower() for v in values]
        setattr(namespace, self.dest, lowercase_values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int)
    parser.add_argument("--controller-url", type=str, default="http://localhost:10000")
    parser.add_argument("--concurrency-count", type=int, default=8)
    parser.add_argument("--model-list-mode", type=str, default="reload", choices=["once", "reload"])
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--moderate", nargs="*", default=[], action=LowercaseAction)
    parser.add_argument("--embed", action="store_true")
    args = parser.parse_args()
    LLAVA.set_args(args)

    demo = build_demo()
    demo.queue(concurrency_count=args.concurrency_count, api_open=False)

    demo.launch(favicon_path="./demo_resources/images/llava_interactive_logo.png")
