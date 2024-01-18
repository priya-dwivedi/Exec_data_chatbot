from openai import OpenAI
import base64
client = OpenAI()

def query_completed_run(thread_id):
        ## Poll all messages from assistant and return them
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        
        # Loop through messages and print content based on role
        message_list = []
        filename = None
        for msg in messages.data:
            role = msg.role
            if role == 'user':
                break
            contents = msg.content
            for content in contents:
                text_content = ''
                if content.type == 'text':
                    text_content = content.text.value
                if content.type == 'image_file':
                    filename = content.image_file.file_id 
                message_list.append(text_content)
    
        
        ## Reverse and return
        message_list.reverse()
        return message_list, filename


def load_fig_from_openai(filename):
    image_data = client.files.content(filename)
    image_data_bytes = image_data.read()
    # Convert image data bytes to a PIL image
    # pil_image = Image.open(io.BytesIO(image_data_bytes))
    # Convert image data bytes to base64-encoded string
    image_data = base64.b64encode(image_data_bytes).decode()

    return image_data