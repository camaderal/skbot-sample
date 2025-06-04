"""Login dialog for handling user authentication via OAuth."""

import os

from botbuilder.dialogs import ComponentDialog, DialogTurnResult, WaterfallDialog, WaterfallStepContext
from botbuilder.dialogs.prompts import OAuthPrompt, OAuthPromptSettings


class LoginDialog(ComponentDialog):
    """
    Dialog to handle user login using OAuth.
    """

    def __init__(self) -> None:
        super(LoginDialog, self).__init__(LoginDialog.__name__)
        self.connection_name = os.getenv("SSO_CONFIG_NAME", "default")
        self.login_success_message = os.getenv("SSO_MESSAGE_SUCCESS", "Login success")
        self.login_failed_message = os.getenv("SSO_MESSAGE_FAILED", "Login failed")

        self.add_dialog(
            OAuthPrompt(
                OAuthPrompt.__name__,
                OAuthPromptSettings(
                    connection_name=self.connection_name,
                    text=os.getenv("SSO_MESSAGE_TITLE"),
                    title=os.getenv("SSO_MESSAGE_PROMPT"),
                    timeout=300000,
                ),
            )
        )

        self.add_dialog(
            WaterfallDialog(
                "WaterfallDialog",
                [self.prompt_step, self.login_step],
            )
        )

        self.initial_dialog_id = "WaterfallDialog"

    async def prompt_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Prompt the user to log in using OAuth.
        """
        return await step_context.begin_dialog(OAuthPrompt.__name__)

    async def login_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Get the token from the previous step.
        """
        token_response = step_context.result
        if token_response:
            await step_context.context.send_activity(self.login_success_message)
            return await step_context.end_dialog()

        await step_context.context.send_activity(self.login_failed_message)
        return await step_context.end_dialog()
