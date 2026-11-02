// Monthly cost budget on the current resource group, with email alerts at 80 % of actual
// spend and 100 % of forecast spend. The amount is in the subscription's billing currency.
// A budget only alerts; it never stops anything. The Static Web App Free plan costs 0, so
// this is a safety net against someone switching the plan to Standard by accident.

targetScope = 'resourceGroup'

@description('Name of the budget.')
param budgetName string = 'budget-webmcp-book'

@description('Monthly amount, in the billing currency.')
@minValue(1)
param amount int = 1

@description('Email address that receives the alerts.')
@minLength(3)
param contactEmail string

@description('First day of the budget period, yyyy-MM-01. Must not change on re-deploys.')
param startDate string = utcNow('yyyy-MM-01')

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: budgetName
  properties: {
    category: 'Cost'
    amount: amount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: startDate
    }
    notifications: {
      actual80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        thresholdType: 'Actual'
        contactEmails: [
          contactEmail
        ]
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        thresholdType: 'Forecasted'
        contactEmails: [
          contactEmail
        ]
      }
    }
  }
}

output name string = budget.name
