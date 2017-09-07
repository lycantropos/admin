from typing import (Union,
                    Dict)

from bson import ObjectId

SerializableType = Union[None, int, bool, float, str, dict, list]
DocumentType = Dict[str, Union[ObjectId,
                               SerializableType]]
