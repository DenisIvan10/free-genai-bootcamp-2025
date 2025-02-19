from aws_cdk import App # type: ignore
from cdk.cdk_stack import CdkStack

app = App()
CdkStack(app, "FrenchStreamlitApp")

app.synth()
