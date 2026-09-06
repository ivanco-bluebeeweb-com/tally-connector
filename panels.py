"""Panel UI for Tally Connector following UI_INTERFACE_STANDARD.md and AUTH_AND_CREDENTIALS_STANDARD.md."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext

def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings",
        variant="secondary",
        size="sm",
        icon="settings",
        on_click=ui.Call("__panel__tally_settings")
    )

def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I set this up?", variant="ghost", size="sm"),
        title="Connecting Tally",
        children=[
            ui.Text(
                "1. Sign in to your Tally account and navigate to API Keys or Integrations settings.\n2. Generate a secure API Key or Access Token (provider API does not offer direct OAuth SSO).\n3. Paste the key below and click Connect.",
                variant="body"
            )
        ]
    )

@ext.panel("tally_sidebar", slot="left")
async def tally_sidebar(ctx, **kwargs) -> ui.UINode:
    return ui.Stack(
        direction="v",
        gap=3,
        align="stretch",
        children=[
            ui.Text("Tally", variant="heading"),
            ui.Stack(
                direction="v",
                gap=1,
                align="stretch",
                children=[
                    ui.Text("Manage your Tally connections and integrations.", variant="caption"),
                ]
            ),
            ui.Divider(),
            ui.Stack(
                direction="v",
                gap=2,
                align="stretch",
                children=[
                    ui.Text("Connect via API Key / Access Token", variant="caption"),
                    ui.Form(
                        submit_label="Connect Tally",
                        action=ui.Call("connect_tally"),
                        children=[
                            ui.Stack(
                                direction="v",
                                gap=2,
                                align="stretch",
                                children=[
                                    ui.Stack(
                                        direction="v",
                                        gap=1,
                                        align="stretch",
                                        children=[
                                            ui.Text("Connection Label", variant="label"),
                                            ui.Input(param_name="label", placeholder="e.g. Production Tally"),
                                        ]
                                    ),
                                    ui.Stack(
                                        direction="v",
                                        gap=1,
                                        align="stretch",
                                        children=[
                                            ui.Text("API Key / Access Token", variant="label"),
                                            ui.Input(param_name="api_key", placeholder="Paste API Key or Access Token"),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                ]
            ),
            _help_modal(),
            ui.Spacer(),
            _settings_button(),
        ]
    )
