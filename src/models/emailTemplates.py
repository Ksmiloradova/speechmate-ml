from enum import Enum


class EmailTemplate(Enum):
    ProjectError = "ProjectError"
    ResetPassword = "ResetPassword"
    SubscriptionAutoRenew = "SubscriptionAutoRenew"
    SubscriptionExpiration = "SubscriptionExpiration"
    SuccessfulProjectCompletion = "SuccessfulProjectCompletion"
    SuccessfulSubscription = "SuccessfulSubscription"
    SuccessfulTokenPurchase = "SuccessfulTokenPurchase"
    UnsuccessfulPayment = "UnsuccessfulPayment"
    Welcome = "Welcome"
