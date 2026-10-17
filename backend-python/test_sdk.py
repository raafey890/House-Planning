from google import genai
import inspect

print("Client init args:")
print(inspect.signature(genai.Client.__init__))
if hasattr(genai.types, 'HttpOptions'):
    print("HttpOptions args:")
    print(inspect.signature(genai.types.HttpOptions))

# Check GenerateContentConfig
print("GenerateContentConfig args:")
print(inspect.signature(genai.types.GenerateContentConfig))
