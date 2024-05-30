param name string
param location string = resourceGroup().location

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  // identity: {
  //   type: 'SystemAssigned'
  // }
  // sku: {
  //   name: 'S0'
  // }
  // kind: 'CognitiveServices'
  properties: {
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
    }
    disableLocalAuth: true
  }
}
