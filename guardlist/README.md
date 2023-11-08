# Guardlist

## Links

- [Wiki](https://microsoft.sharepoint-df.com/teams/UniversalGuardListWiki)
- [Repo](https://office.visualstudio.com/OC/_git/Guardlist?path=/README.md&_a=preview)
- [Text Page](https://hedwigtestserver.blob.core.windows.net/master/guardlistTestPage.html)
- [Sample Response](https://office.visualstudio.com/OC/_git/Guardlist?path=/README.md&_a=preview&anchor=metadata-usage)

## Setup

Set secret GUID for API access. Ask mattm@microsoft.com

## Install Guardlist python package

```bash
pip install GuardlistPython==0.4.12
```

> Note: This currently requires manual authentication using a browser.

```bash
Looking in indexes: https://office.pkgs.visualstudio.com/_packaging/Office/pypi/simple/
[Warning] [CredentialProvider]Warning: Cannot persist Microsoft authentication token cache securely!
[Warning] [CredentialProvider]Warning: Using plain-text fallback token cache
[Minimal] [CredentialProvider]DeviceFlow: https://office.pkgs.visualstudio.com/_packaging/Office/pypi/simple/
[Minimal] [CredentialProvider]ATTENTION: User interaction required.

    **********************************************************************

    To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code APTJ8RU67 to authenticate.

    **********************************************************************

[Information] [CredentialProvider]VstsCredentialProvider - Acquired bearer token using 'MSAL Device Code'
[Information] [CredentialProvider]VstsCredentialProvider - Attempting to exchange the bearer token for an Azure DevOps session token.
Collecting GuardlistPython==0.4.12
  Downloading https://office.pkgs.visualstudio.com/_packaging/86ec7889-a365-4cd1-90df-6e18cc2ea59f/pypi/download/guardlistpython/0.4.12/GuardlistPython-0.4.12-py3-none-any.whl (39.6 MB)
```

## Run

```bash
python -m guardlist \
  --input_text "Is this text safe?"
```
