from .assistant import Assistant
from .listeners import StreamingPrinter, Printer


class AssistantTest:

    def __init__(self):
        self.a = Assistant(
            "You generate text.",
            listeners=[StreamingPrinter()],
            functions=[self.weather],
            stream=True,
        )

    def run(self):
        x = self.a.query(
            "tell me what model you are before making any function calls.  And what's the weather in Boston?",
            None,
        )
        print(x)

    def weather(self, location, unit="f"):
        """
        {
            "name": "get_weather",
            "description": "Determine weather in my location",
            "parameters": {
                "type": "object",
                "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": [
                    "c",
                    "f"
                    ]
                }
                },
                "required": [
                "location"
                ]
            }
        }
        """
        return f"weather({location}, {unit})", "Sunny and 72 degrees."


t = AssistantTest()
t.run()