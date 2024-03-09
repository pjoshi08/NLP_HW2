import datetime
import os.path
from typing import AnyStr, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gentopia.tools.basetool import *


class GoogleCalenderData(BaseTool):
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class GoogleCalenderArgs(BaseModel):
    events: str = Field(..., description="calender events")

class GoogleCalendarTool(GoogleCalenderData):
    """Tool that retrieves upcoming events from Google Calendar."""

    name = "google_calendar_tool"
    description = "A tool to retrieve upcoming events from Google Calendar."
    args_schema: Optional[Type[BaseModel]] = GoogleCalenderArgs

    def _run(self, events: AnyStr) -> AnyStr:
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("calendar", "v3", credentials=creds)
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                return "No upcoming events found."

            whole = ""
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))                
                whole += start + event["summary"] + "\n"

            return whole

        except HttpError as error:
            return f"An error occurred: {error}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "__main__":
    ans = GoogleCalendarTool()._run()
    print(ans)
