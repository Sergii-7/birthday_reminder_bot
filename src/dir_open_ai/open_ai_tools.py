from pyexpat.errors import messages
from typing import Optional, List, Dict, Any, Union
from openai.types.chat import ChatCompletion
from src.dir_open_ai.connect import client
from src.dir_open_ai.service_openai import encode_image
from src.service.loggers.py_logger_openai import get_logger

logger = get_logger(__name__)


class ResponseTextAI:
    """ Class for getting content:(str) from AI """

    def __init__(
            self, role: str = None, prompt_for_ai: Optional[str] = None,
            messages_for_ai: Optional[List[Dict[str, Any]]] = None):
        """ Create messages for AI """
        if not prompt_for_ai and not messages_for_ai:
            self.messages = None
        elif prompt_for_ai:
            role = role if role else "Ти корисний помічник, який допомагає мені з будь-якими питаннями."
            self.messages = [
                {"role": "system", "content": role},
                {"role": "user", "content": prompt_for_ai}
            ]
        else:
            self.messages = messages

    async def get_content(
            self, model: str = "gpt-4-turbo-2024-04-09", max_tokens: int = 500, temperature: float = 0
    ) -> Dict[str, Union[str, int]]:
        """ Get content from AI """
        if self.messages is None:
            return {"error": "prompt and messages are both None"}

        try:
            logger.info("Start ResponseTextAI()")
            response: ChatCompletion = await client.chat.completions.create(
                model=model,
                messages=self.messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            # print(response)
            print(response.choices[0].message.content)
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        except Exception as e:
            logger.error(f"Error occurred in ResponseTextAI: {str(e)}")
            return {"error": str(e)}


class ResponseImageAI:
    """ Class for working with OpenAI API: we send text and image or get image """

    async def get_image_from_ai(self, prompt_for_ai: str) -> Dict[str, Optional[Union[str, int]]]:
        """ Get url for Image from AI """
        try:
            logger.info("Start get_image_from_ai")
            response = await client.images.generate(
                model="dall-e-3",
                prompt=prompt_for_ai,
                size="1024x1024",
                quality="standard",
                n=1  # не можна змінювати
            )
            # print(response)
            return {"image_url": response.data[0].url, "revised_prompt": response.data[0].revised_prompt,}
        except Exception as e:
            logger.error(e)
            return {"error": str(e)}

    def get_messages_with_image(
            self, prompt_for_ai: str, image_path: Optional[str] = None, url_: Optional[str] = None
    ) -> Optional[List[Dict[str, Union[Any]]]]:
        """ Create Dict with image data for messages """
        data_image = None
        if image_path:
            base64_image = encode_image(image_path=image_path)
            if base64_image:
                data_image = f"data:image/jpeg;base64,{base64_image}"
        else:
            data_image = url_
        if data_image:
            messages_for_ai = [{"role": "user", "content": [{"type": "text", "text": prompt_for_ai},
                                                     {"type": "image_url", "image_url": {"url": data_image},},],},]
            return messages_for_ai
        return None

    async def get_response(
            self, prompt_for_ai: str, image_path: Optional[str] = None, url_: Optional[str] = None,
            max_tokens: int = 2000, temperature: float = 0
    ) -> Dict[str, Optional[Union[str, int]]]:
        """
        Send image for AI with text
        - type_image: (str) "image_url" | "image_file"
        - image_path: Optional[str]
        - text: (str)
        """
        messages_for_ai = self.get_messages_with_image(prompt_for_ai=prompt_for_ai, url_=url_, image_path=image_path)
        if messages_for_ai:
            try:
                logger.info("Start ResponseImageAI()")
                response: ChatCompletion = await client.chat.completions.create(
                    model="gpt-4-turbo-2024-04-09",  # модель для отримання зображень
                    messages=messages_for_ai,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                # print(response)
                return {
                    "content": response.choices[0].message.content,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            except Exception as e:
                result = str(e)
        else:
            result = "Not Start ResponseImageAI()"
        logger.error(result)
        return {"error": result}



# from asyncio import run as asyncio_run
# from config import media_file_path
# prompt_for_ai = ("Напиши короткий текст для Сергія від імені команди Аврора з проханням здати гроші на день "
#                  "народження колеги Андрія. Поясни, що він досі цього не зробив, але без звинувачень або агресії. "
#                  "Текст має бути жорстким та однозначним, і одразу підходити для відправки.")
# start_ai = ResponseTextAI(prompt_for_ai=prompt_for_ai)
# res = asyncio_run(main=start_ai.get_content(temperature=1))
# print(res)
# start_ai_with_image = ResponseImageAI()
# res = asyncio_run(start_ai_with_image.get_response(
#     image_path=f"{media_file_path}images/chat_photo.jpg", prompt_for_ai="Скажи мені що тут на фото"))
# prompt = "Зроби мені зображення як колега по роботі не хоче бути членом команди і шкодить нашої компанії."
# res  =asyncio_run(main=start_ai_with_image.get_image_from_ai(prompt_for_ai=prompt))
# print(res)

"""
ImagesResponse(
    created=1728221518, 
    data=[Image(b64_json=None, revised_prompt='Create an image depicting a corporate scenario where a co-worker, a Caucasian male, is acting in an uncooperative manner, resulting in detrimental effects to the company. The office environment should be clear and there should be visible signs of distress among other team members, a diverse group of South Asian female, Black male, and Middle-Eastern female colleagues.', url='https://oaidalleapiprodscus.blob.core.windows.net/private/org-vdPphsiIVBT6qImMmNI4a2DJ/user-hr3lMNoxppiZgKqs7CP2YZo9/img-yTHQhVf3EOBgTM09XHOmUtpw.png?st=2024-10-06T12%3A31%3A58Z&se=2024-10-06T14%3A31%3A58Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2024-10-06T09%3A34%3A25Z&ske=2024-10-07T09%3A34%3A25Z&sks=b&skv=2024-08-04&sig=QvC5ys6T4v44P%2BJpo5GGDbSPxTuHrJo8/aXzLSaEqas%3D')])

--------------------------

ChatCompletion(
    id='chatcmpl-AFKAnrucPH8Hu75femZZVTOmoASxt', 
    choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='На зображенні немає жодного тексту, включаючи e-mail. Я бачу лише святковий торт зі свічками та феєрверками. Якщо у вас є інші питання про зображення, будь ласка, задайте їх!', refusal=None, role='assistant', function_call=None, tool_calls=None))], 
    created=1728215829, model='gpt-4-turbo-2024-04-09', object='chat.completion', service_tier=None, system_fingerprint='fp_81dd8129df', 
    usage=CompletionUsage(completion_tokens=95, prompt_tokens=794, total_tokens=889, completion_tokens_details=CompletionTokensDetails(audio_tokens=None, reasoning_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=None, cached_tokens=0))
)
"""

