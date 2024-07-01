from dotenv import load_dotenv
import base64
from langchain.chains.transform import TransformChain
from langchain.chat_models.openai import ChatOpenAI
from langchain_core.runnables import chain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,
)


def load_image(inputs: dict) -> dict:
    """Load image from file and encode it as base64."""
    image_path = inputs["image_path"]

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    image_base64 = encode_image(image_path)
    return {"image": image_base64}


load_image_chain = TransformChain(
    input_variables=["image_path"], output_variables=["image"], transform=load_image
)


class ImageInformation(BaseModel):
    """Information about an image."""

    image_caption: str = Field(description="Image Caption describing the image")


parser = CommaSeparatedListOutputParser()


@chain
def image_model(inputs: dict) -> str | str | dict:
    """Invoke model with image and prompt."""
    model = ChatOpenAI(temperature=0.1, model="gpt-4o")
    msg = model.invoke(
        [
            SystemMessage(
                content="""
                    Role: Automobile Photography Expert

                    Task: Assist user with crafting captions for their automobile photographs.

                    Knowledge:
                    Extensive knowledge of automobile photography techniques and aesthetics.
                    Understanding of car design, features, and terminology.

                    Goal:
                    Generate informative captions that can be used to tain Text to Image Models.
                """
            ),
            HumanMessage(
                content=[
                    {"type": "text", "text": inputs["prompt"]},
                    {"type": "text", "text": parser.get_format_instructions()},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{inputs['image']}"
                        },
                    },
                ]
            ),
        ]
    )
    return msg.content


def main():
    vision_prompt = """
    Image Caption Generation Task
    Input: An image of a car.

    Target Object: The car in the image is a Toyota Corolla Cross XLE 2022.

    Desired Output:

    Multiple captions describing the image, each including:
    Background information about the setting or scene.
    Color of the Toyota Corolla Cross XLE 2022 in the image.
    Description of the photography angles used (e.g., close-up shot, wide shot, side profile).
    Note: These captions are intended for training text-to-image models.
    Example Captions:

    A sleek, silver Toyota Corolla Cross XLE 2022 parked on a scenic mountain road, captured in a wide shot that showcases the breathtaking backdrop. (This caption describes the background, car color, and photo angle.)
    A detailed close-up of a red Toyota Corolla Cross XLE 2022 headlight, highlighting the intricate design elements. (This caption describes the car color, photo angle, and a specific detail.)
    """
    vision_chain = load_image_chain | image_model | parser

    for i in range(2, 163):
        ipath = f"train-images/{str(i).zfill(3)}.jpg"
        opath = f"train-images/{str(i).zfill(3)}.txt"
        data = vision_chain.invoke({"image_path": f"{ipath}", "prompt": vision_prompt})
        data = ", ".join(data)
        with open(opath, "wb") as ofile:
            ofile.write(data.encode("utf-8"))


if __name__ == "__main__":
    load_dotenv()
    main()
