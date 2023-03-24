import enum

class Align(enum.Enum):
    Mid_Center = (1, 1)
    Mid_Right = (1, 2)
    Mid_Left = (1, 0)
    Top_Center = (0, 1)
    Top_Right = (0, 2)
    Top_Left = (0, 0)
    Bottom_Center = (2, 1)
    Bottom_Right = (2, 2)
    Bottom_Left = (2, 0)

class EventType(enum.Enum):
    Mouse_Touch_End = 0

class EventParam(enum.Enum):
    x = 'x'
    y = 'y'