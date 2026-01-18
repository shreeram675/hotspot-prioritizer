import httpx
import asyncio
import io

GARBAGE_CHILD_URL = "http://ai-garbage-child:8002"

async def test_child():
    print(f"Testing connection to {GARBAGE_CHILD_URL}...")
    
    # Create dummy image (100x100 white square)
    dummy_image = b'\xff' * 10000 
    # That's not a valid JPEG/PNG. Let's try to send simple bytes that might pass or fail gracefully.
    # Actually, let's use a minimal valid JPG header if possible, or just random bytes.
    # The PIL.Image.open might fail if it's not a real image.
    
    # Better: Use a real tiny white pixel
    # 1x1 white pixel JPEG base64 decoded
    import base64
    valid_jpg = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvavynLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==')
    
    async with httpx.AsyncClient() as client:
        try:
            print("\n1. Testing /analyze_image (Simulated/YOLO)...")
            files = {'image': ('test.jpg', valid_jpg, 'image/jpeg')}
            resp = await client.post(f"{GARBAGE_CHILD_URL}/analyze_image", files=files, timeout=10.0)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text}")
            
            print("\n2. Testing /analyze_scene (Simulated/CNN)...")
            files2 = {'image': ('test.jpg', valid_jpg, 'image/jpeg')}
            resp2 = await client.post(f"{GARBAGE_CHILD_URL}/analyze_scene", files=files2, timeout=10.0)
            print(f"Status: {resp2.status_code}")
            print(f"Body: {resp2.text}")

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_child())
