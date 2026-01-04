#!/usr/bin/env python3
"""
Kangxi Radical to Semantic Category Mapping

The 214 Kangxi radicals mapped to our semantic categories.
This provides a reliable Chinese-native categorization fallback.
"""

# Radical number -> (Root, Primary) or (Root, Primary, Subcategory)
KANGXI_RADICAL_TO_CATEGORY = {
    # === NATURE > ANIMALS ===
    # Beast/Mammal radicals
    94: ('Nature', 'Animals', 'Mammals'),   # 犭 犬 dog
    93: ('Nature', 'Animals', 'Mammals'),   # 牛 cow/ox
    123: ('Nature', 'Animals', 'Mammals'),  # 羊 sheep
    152: ('Nature', 'Animals', 'Mammals'),  # 豕 pig
    153: ('Nature', 'Animals', 'Mammals'),  # 豸 cat/badger
    187: ('Nature', 'Animals', 'Mammals'),  # 馬 horse
    198: ('Nature', 'Animals', 'Mammals'),  # 鹿 deer
    
    # Bird radicals
    196: ('Nature', 'Animals', 'Birds'),    # 鳥 bird
    172: ('Nature', 'Animals', 'Birds'),    # 隹 short-tailed bird
    
    # Fish/Aquatic radicals
    195: ('Nature', 'Animals', 'Fish'),     # 魚 fish
    
    # Insect radicals
    142: ('Nature', 'Animals', 'Insects'),  # 虫 insect/worm
    
    # Reptile/Amphibian radicals
    205: ('Nature', 'Animals', 'Amphibians'),  # 黽 frog
    213: ('Nature', 'Animals', 'Reptiles'),    # 龜 turtle
    212: ('Nature', 'Animals', 'Mythical'),    # 龍 dragon
    
    # Shell (often used for mollusks/money)
    154: ('Society', 'Economy'),            # 貝 shell/money
    
    # === NATURE > PLANTS ===
    140: ('Nature', 'Plants', 'Grasses'),   # 艸 艹 grass/herb
    75: ('Nature', 'Plants', 'Trees'),      # 木 tree/wood
    115: ('Nature', 'Plants', 'Grasses'),   # 禾 grain
    118: ('Nature', 'Plants'),              # 竹 bamboo
    119: ('Nature', 'Plants', 'Grasses'),   # 米 rice
    201: ('Nature', 'Plants'),              # 黃 yellow (often plants)
    
    # === NATURE > ELEMENTS ===
    # Water
    85: ('Nature', 'Elements', 'Water'),    # 水 氵 water
    
    # Fire
    86: ('Nature', 'Elements'),             # 火 灬 fire
    
    # Earth/Stone/Metal
    32: ('Nature', 'Elements', 'Landforms'),  # 土 earth
    46: ('Nature', 'Elements', 'Landforms'),  # 山 mountain
    112: ('Nature', 'Elements', 'Minerals'),  # 石 stone
    167: ('Nature', 'Elements', 'Minerals'),  # 金 钅 metal/gold
    96: ('Nature', 'Elements', 'Minerals'),   # 玉 jade (precious stone)
    
    # === NATURE > WEATHER ===
    173: ('Nature', 'Weather'),             # 雨 rain
    72: ('Nature', 'Weather'),              # 日 sun (also time)
    74: ('Nature', 'Weather'),              # 月 moon (also body)
    
    # === HUMAN > BODY ===
    130: ('Human', 'Body', 'Body Parts'),   # 肉 月 meat/flesh (body radical)
    61: ('Human', 'Emotions'),              # 心 忄 heart (emotions)
    109: ('Human', 'Body', 'Sense Organs'), # 目 eye
    128: ('Human', 'Body', 'Sense Organs'), # 耳 ear
    30: ('Human', 'Body', 'Face'),          # 口 mouth
    132: ('Human', 'Body'),                 # 自 self/nose
    188: ('Human', 'Body', 'Skeleton'),     # 骨 bone
    190: ('Human', 'Body', 'Covering'),     # 髟 hair
    64: ('Human', 'Actions'),               # 手 扌 hand (actions)
    157: ('Human', 'Body', 'Limbs'),        # 足 foot
    
    # === HUMAN > ACTIONS ===
    66: ('Human', 'Actions'),               # 攴 攵 strike/tap
    76: ('Human', 'Actions'),               # 欠 yawn/lack
    77: ('Human', 'Actions'),               # 止 stop/foot
    162: ('Human', 'Actions'),              # 辵 辶 walk/movement (HIGH YIELD - 进退送达等)
    156: ('Human', 'Actions'),              # 走 run/walk
    60: ('Human', 'Actions'),               # 彳 step (往待律等)
    54: ('Human', 'Actions'),               # 廴 stride
    135: ('Human', 'Actions'),              # 舌 tongue (lick, etc.)
    138: ('Human', 'Actions'),              # 艮 boundary/limit (根, 很, 跟)
    70: ('Human', 'Actions'),               # 方 square/direction
    
    # === HUMAN > RELATIONS ===
    9: ('Human', 'Relations'),              # 人 亻 person
    10: ('Human', 'Relations'),             # 儿 legs/person
    38: ('Human', 'Relations', 'Family'),   # 女 woman
    39: ('Human', 'Relations', 'Family'),   # 子 child
    
    # === HUMAN > EMOTIONS ===
    # (61 heart already listed above)
    
    # === SOCIETY > GOVERNMENT ===
    163: ('Society', 'Government'),         # 邑 阝(right) city
    170: ('Society', 'Government'),         # 阜 阝(left) mound/hill (often places)
    
    # === SOCIETY > ECONOMY ===
    # (154 shell already listed above)
    
    # === SOCIETY > RELIGION ===
    113: ('Society', 'Religion'),           # 示 礻 spirit/altar
    
    # === OBJECTS > TOOLS ===
    62: ('Objects', 'Tools', 'Weapons'),    # 戈 halberd/weapon
    181: ('Objects', 'Tools'),              # 頁 head/page
    18: ('Objects', 'Tools', 'Weapons'),    # 刀 刂 knife
    57: ('Objects', 'Tools', 'Weapons'),    # 弓 bow
    110: ('Objects', 'Tools', 'Weapons'),   # 矛 spear
    159: ('Objects', 'Tools', 'Vehicles'),  # 車 cart/vehicle
    137: ('Objects', 'Tools'),              # 舟 boat
    127: ('Objects', 'Tools'),              # 耒 plow

    # === OBJECTS > CLOTHING ===
    145: ('Objects', 'Tools', 'Clothing'),  # 衣 衤 clothes (HIGH YIELD - 衫袖被等)
    120: ('Objects', 'Tools', 'Textiles'),  # 糸 纟 silk/thread
    178: ('Objects', 'Tools', 'Clothing'),  # 韋 leather
    177: ('Objects', 'Tools', 'Clothing'),  # 革 leather/hide

    # === OBJECTS > BUILDINGS ===
    40: ('Objects', 'Buildings'),           # 宀 roof (HIGH YIELD - 家室宮等)
    53: ('Objects', 'Buildings'),           # 广 shelter
    169: ('Objects', 'Buildings'),          # 門 gate/door
    63: ('Objects', 'Buildings'),           # 戶 door/household

    # === OBJECTS > CONTAINERS ===
    108: ('Objects', 'Containers'),         # 皿 dish/vessel

    # === OBJECTS > FOOD ===
    184: ('Objects', 'Food'),               # 食 飠 food/eat
    192: ('Objects', 'Food'),               # 鬯 sacrificial wine
    193: ('Objects', 'Food'),               # 鬲 cauldron
    164: ('Objects', 'Food'),               # 酉 wine vessel/alcohol

    # === COMMUNICATION > LANGUAGE ===
    149: ('Communication', 'Language'),     # 言 訁 speech/words

    # === COMMUNICATION > ARTS ===
    100: ('Communication', 'Arts'),         # 生 life/birth (often music)

    # === ABSTRACT > QUALITIES ===
    # Quality-related radicals that might be miscategorized

    # === ABSTRACT > TIME ===
    # (日 sun already in Weather - could dual map)
}

def get_category_from_radical(radical_num: int) -> tuple | None:
    """Get category tuple from radical number."""
    return KANGXI_RADICAL_TO_CATEGORY.get(radical_num)

if __name__ == '__main__':
    # Test
    print("Radical 94 (dog):", get_category_from_radical(94))
    print("Radical 140 (grass):", get_category_from_radical(140))
    print("Radical 85 (water):", get_category_from_radical(85))
    print("Radical 61 (heart):", get_category_from_radical(61))
    print("Radical 9 (person):", get_category_from_radical(9))
    
    # Count coverage
    print(f"\nTotal radicals mapped: {len(KANGXI_RADICAL_TO_CATEGORY)}")

