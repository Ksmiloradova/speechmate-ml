from datetime import datetime

import openai

from configs.env import OPEN_AI_API_KEY
from configs.logger import print_info_log, catch_error
from constants.log_tags import LogTag

# Set OpenAI API key
openai.api_key = OPEN_AI_API_KEY

gpt_model = "gpt-4"
# gpt_model = "gpt-3.5-turbo"

translation_gpt_prompt = """
You are a professional text translator.
You understand the meaning of the text well.
You are able to select the most appropriate formulations so that they fit the context of the text you are translating.
I need you to translate the text below to {language} language.
If the text is already in {language}, you must write this text in the answer without translation.
If you are not able to translate this text, you must write this text in the answer without translation.
You must remain all [] symbols on their places in original text.
Your answer must be only translated text.

The text you need to translate to {language} language:
{text_chunk}
"""


def translate_text_chunk_with_gpt(
    language: str,
    text_chunk: str,
    project_id: str,
    show_logs: bool
) -> str:
    """
    Translates a given text into the specified language using OpenAI's model.

    :param language: The target language for translation.
    :param text_chunk: The text chunks to be translated.
    :param project_id: The id of the processing project.
    :param show_logs: Determines whether to display logs while translating with gpt.

    Returns:
    - str: Translated text or original text if translation is not possible.
      """

    try:
        if show_logs:
            print_info_log(
                tag=LogTag.TRANSLATE_TEXT_CHUNK_WITH_GPT,
                message=f"Translating text chunk: '{text_chunk}'"
            )

        query_content = translation_gpt_prompt.format(
            language=language,
            text_chunk=text_chunk
        )
        response = openai.ChatCompletion.create(
            model=gpt_model,
            messages=[{
                "role": "user",
                "content": query_content
            }],
        )
        request_time = datetime.now()
        translated_text = response['choices'][0]['message']['content']
        response_time = datetime.now()
        time_difference = response_time - request_time

        if show_logs:
            print_info_log(
                tag=LogTag.TRANSLATE_TEXT_CHUNK_WITH_GPT,
                message=f"Text chunk translated:  {translated_text}"
            )
            print_info_log(
                tag=LogTag.TRANSLATE_TEXT_CHUNK_WITH_GPT,
                message=f"Response time is {time_difference}"
            )

        return translated_text

    except Exception as e:
        catch_error(
            tag=LogTag.TRANSLATE_TEXT_CHUNK_WITH_GPT,
            error=e,
            project_id=project_id
        )
