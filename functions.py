from variables import *
from pathlib import Path
import pickle
import copy


def choose_equipment(equipment_options, number_elements=1):
    """
    It loops through the list of possible equipments, given, for each possible
    choice of it, the possibility to the user to select the one desired.
    :param equipment_options: A list containing the possible choices for the
    user. Every choice that it has is a list inside of it, if there is a hard
    group inside of it, it must be in a tuple, if the tuple is only one element
    it must be created by the keyword tuple().
    :param number_elements: Number of the elements that will be chosen
    :return: List of equipments chosen by the user.
    """
    copy_list = copy.deepcopy(equipment_options)
    already_chosen = []
    last_chosen = None
    equipments = []

    for _ in range(number_elements):
        error = False
        item_number = 0
        choice = None

        try:
            choice = copy_list[item_number]
        except IndexError:
            error = True

        while not error:
            if ['GO BACK', 'EXIT'] not in choice:
                choice.append(['GO BACK', 'EXIT'])
            chosen = None
            valid_choice = False
            group_number = 1
            groups = {}
            text = ''

            # Tuples represent a group of more than one object that must be
            # chose together, so it prints all of them with only one number
            if tuple_inside_list(choice):
                tuples = []
                no_tuples = []

                for group in choice:
                    if isinstance(group, tuple):
                        tuples.append(group)
                    else:
                        no_tuples += list_with_no_list_or_dict(group)

                no_tuples = [no_tuples]
                choice = tuples + no_tuples

                text += 'You have to chose between:\n'
                for group in choice:
                    if isinstance(group, tuple):
                        pack_name = None
                        groups[str(group_number)] = group

                        group_item_names = []
                        for item in group:
                            group_item_names.append(item.name)

                        for pack, items in packs.items():
                            is_pack = True
                            for item in items:
                                if item.name not in group_item_names:
                                    is_pack = False

                            if is_pack:
                                pack_name = pack

                        if pack_name is not None:
                            text += (
                                f'Or group {group_number} '
                                f'({pack_name.title()}):\n')
                        else:
                            text += f'Or group {group_number}:\n'
                        elements = {}
                        for element in group:
                            if element not in elements:
                                elements[element] = 1
                            else:
                                elements[element] += 1

                        for element, units in elements.items():
                            text += f'- {element.name.title()} x{units}\n'

                        group_number += 1

                    else:
                        text += 'Or any of these:\n'
                        for item in group:
                            if type(item) is not str:
                                text += (f'({group_number}) '
                                         f'{item.name.title()}\n')
                            else:
                                text += f'({group_number}) {item.title()}\n'

                            groups[str(group_number)] = item
                            group_number += 1
                    text += '\n'
            # When there's no tuple, every element's a possible choice alone
            else:
                choice = list_with_no_list_or_dict(choice)
                text += 'Choose one of the following options:\n'

                for item in choice:
                    if type(item) is not str:
                        if item.name != 'UNARMED ATTACK':
                            text += f'({group_number})' \
                                    f' {item.name.title()}\n'
                    else:
                        text += f'({group_number}) {item.title()}\n'

                    groups[str(group_number)] = item
                    group_number += 1

            # Asks and checks the value given by the user
            choice = list_with_no_list_or_dict(choice)
            while not valid_choice:
                if len(equipments) != 0:
                    elements = {}
                    for element in equipments:
                        if element not in elements:
                            elements[element] = 1
                        else:
                            elements[element] += 1

                    print(f'You have chosen so far:')

                    for item, units in elements.items():
                        print(f'- {item.name.title()} x{units}')

                    print('')

                print(text)
                chosen = input('Type the number of the chosen one: ')

                if chosen.isnumeric() and chosen in groups:
                    valid_choice = True

                    if groups[chosen] != 'EXIT' \
                            and groups[chosen] != 'GO BACK':
                        item_number += 1
                        chosen = groups[chosen]
                        choice.remove(chosen)

                    elif groups[chosen] == 'GO BACK':
                        if len(equipments) > 0:
                            item_number -= 1
                            if isinstance(last_chosen, list):
                                for item in last_chosen:
                                    equipments.remove(item)
                            else:
                                equipments.remove(last_chosen)

                                already_chosen.pop()
                                if len(already_chosen) > 0:
                                    last_chosen = already_chosen[-1]
                                else:
                                    last_chosen = None

                        else:
                            return 'GO BACK'

                    elif groups[chosen] == 'EXIT':
                        return 'EXIT'

                else:
                    print('\nSorry, not a valid number. Please try again.')

            if not isinstance(chosen, str):
                already_chosen.append(chosen)
                last_chosen = chosen

                if isinstance(chosen, tuple):
                    chosen = create_simple_list(chosen)
                else:
                    chosen = [chosen]

                equipments += chosen

            clear_terminal()
            try:
                choice = copy_list[item_number]
            except IndexError:
                error = True

    return equipments


def buy_equipment(starting_wealth, fixed_price=True):
    equipments = []
    wealth = starting_wealth

    finished = False
    while not finished:
        dictionary = index['EQUIPMENT'].copy()
        visited = []
        end = False
        wealth = starting_wealth
        equipments = []

        while not end:
            clear_terminal()

            options = {}
            selection_number = 1
            for name, item in dictionary.items():
                if isinstance(item, dict):
                    key = f'{name}'
                else:
                    # If it isn't a dictionary, it's a object possible to choose
                    key = f'{name:27s}' \
                          f'Cost (gp): {str(item.cost):18s}' \
                          f'Weight (lb.): {item.weight:2.2f}' \
 \
                            options[key] = item
                selection_number += 1

            selected = select(
                options=options,
                prompt=f'You have {wealth} gp to spend in equipment\n'
                       f'You can choose in the options for equipment:',
                show_type='key',
                return_type='value',
                single_item=True
            )

            if isinstance(selected, dict):
                if dictionary not in visited:
                    visited.append(dictionary)
                dictionary = selected

            elif selected == 'GO BACK':
                if len(visited) >= 1:
                    dictionary = visited[-1]
                    visited.remove(dictionary)
                else:
                    return ['GO BACK', 'GO BACK']

            elif selected == 'EXIT':
                end = True

            else:
                # A item was selected
                if fixed_price:
                    price = selected.cost
                else:
                    price = get_a_number(
                        'The price suggested for this item in the Player\'s'
                        f'Handbook is of {selected.cost} gp.\n'
                        'How much are you paying for it?'
                    )

                if price is not None:
                    if wealth - price >= 0:
                        equipments.append(selected)
                        wealth -= price
                        wealth = round(wealth, 2)

                        if wealth == 0:
                            end = True

                    else:
                        # The user bought a item, but could not afford it.
                        print('')
                        print(
                            "Sorry. It appears you don't have the means "
                            'necessaries to buy this item. Please try again or '
                            'type BACK or EXIT'
                        )

        clear_terminal()
        options = ['CONFIRM', 'RESTART']
        choice = select(
            options=options,
            prompt='You finished shopping for equipments.\n'
                   'Select what to do now.',
            single_item=True,
            go_back=False,
        )

        if choice != 'RESTART':
            finished = True

            if choice == 'EXIT':
                equipments = None
                wealth = None

    return [equipments, wealth]


def random_trinket():
    trinkets = [
        Trinket('Mummified goblin hand'),
        Trinket('Piece of crystal that faintly glows in the moonlight'),
        Trinket('Gold coin minted in an unknown land'),
        Trinket('Diary written in a language you don\'t know'),
        Trinket('Brass ring that never tarnishes'),
        Trinket('Old chess piece made from glass'),
        Trinket(
            'Pair of knucklebone dice, each with a skull symbol on the side '
            'that would normally show six pips'
        ),
        Trinket(
            'Small idol depicting a nightmarish creature that gives you '
            'unsettling dreams when you sleep near it'
        ),
        Trinket('Rope necklace from which dangles four mummified elf fingers'),
        Trinket('Deed for a parcel of land in a realm unknown to you'),
        Trinket('1-ounce block made from an unknown material'),
        Trinket('Small cloth doll skewered with needles'),
        Trinket('A tooth form an unknown beast'),
        Trinket('Enormous scale, perhaps from a dragon'),
        Trinket('Bright green feather'),
        Trinket('Old divination card bearing your likeness'),
        Trinket('Glass orb filled with moving smoke'),
        Trinket('1-pound egg with a bright red shell'),
        Trinket('Pipe that blows bubbles'),
        Trinket(
            'Glass jar containing a weird bit of flesh floating '
            'in pickling fluid'
        ),
        Trinket(
            'A tiny gnome-crafted music box that plays a song you dimly '
            'remember from your childhood'
        ),
        Trinket('Small wooden statuette of a smug halfling'),
        Trinket('Brass orb etched with strange runes'),
        Trinket('Multicolored stone disk'),
        Trinket('Tiny silver icon of a raven'),
        Trinket(
            'Bag containing forty-seven humanoid teeth, '
            'one of which is rotten'
        ),
        Trinket('Shard of obsidian that always feels warm to the touch'),
        Trinket('Dragon\'s bony talon hanging from a plain leather necklace'),
        Trinket('Pair of old socks'),
        Trinket(
            'Blank book whose pages refuse to hold any substance of marking'
        ),
        Trinket('Silver badge in the shape of a five-pointed star'),
        Trinket('Knife that belonged to a relative'),
        Trinket('Glass vial filled with nail clippings'),
        Trinket(
            'Rectangular metal device with two tiny metal cups on one end '
            'that throws sparks when wet'
        ),
        Trinket('White, sequined glove sized for a human'),
        Trinket('Vest with one hundred tiny pockets'),
        Trinket('Small, weightless stone block'),
        Trinket('Tiny sketch portrait of a goblin'),
        Trinket('Empty glass vial that smells of perfume when opened'),
        Trinket(
            'Gemstone that looks like a lump of coal when '
            'examined by anyone but you'
        ),
        Trinket('Scrap of cloth from an old banner'),
        Trinket('Rank insignia from a lost legionnaire'),
        Trinket('Tiny silver bell without a clapper'),
        Trinket('Mechanical canary inside a gnomish lamp'),
        Trinket(
            'Tiny chest carved to look like it has '
            'numerous feet on the bottom'
        ),
        Trinket('Dead sprite inside a clear glass bottle'),
        Trinket(
            'Metal can that has no opening but sounds as if it is filled with'
            'liquid , sand, spiders, or broken glass (your choice)'),
        Trinket(
            'A glass orb filled with water, in '
            'which swims a clockwork goldfish'
        ),
        Trinket('Silver spoon with an M engraved on the handle'),
        Trinket('Whistle made from gold-colored wood'),
        Trinket('Dead scarab beetle the size of your hand'),
        Trinket('Two toy soldiers, one with a missing head'),
        Trinket('Small box filled with different-sized buttons'),
        Trinket('Candle that can\'t be lit'),
        Trinket('Tiny cage with no door'),
        Trinket('Old key'),
        Trinket('Indecipherable treasure map'),
        Trinket('Hilt from a broken sword'),
        Trinket('Rabbit\'s foot'),
        Trinket('Glass eye'),
        Trinket('Cameo carved in the likeness of a hideous person'),
        Trinket('Silver skull the size of a coin'),
        Trinket('Alabaster mask'),
        Trinket('Pyramid of sticky black incense that smells very bad'),
        Trinket('Nightcap that, when worn, gives you pleasant dreams'),
        Trinket('Single caltrop made from bone'),
        Trinket('Gold monocle frame without the lens'),
        Trinket('A 1-inch cube, each side painted a different color'),
        Trinket('Crystal knob from a door'),
        Trinket('Small packet filled with pink dust'),
        Trinket(
            'Fragment of a beautiful song, written as '
            'musical notes on two pieces of parchment'
        ),
        Trinket('Silver teardrop earring made from a real teardrop'),
        Trinket(
            'Shell of an egg painted with scenes of '
            'human misery in disturbing detail'
        ),
        Trinket('Fan that, when unfolded, shows a sleeping cat'),
        Trinket('Set of bone pipes'),
        Trinket(
            'Four-leaf clover pressed inside a book '
            'discussing manners and etiquette'
        ),
        Trinket(
            'Sheet of parchment upon which is drawn '
            'a complex mechanical contraption'
        ),
        Trinket('Ornate scabbard that fits no blade you have found so far'),
        Trinket('Invitation to a party where a murder happened'),
        Trinket(
            'Bronze pentacle with an etching of a rat\'s head in its center'
        ),
        Trinket(
            'Purple handkerchief embroidered with '
            'the name of a powerful archmage'
        ),
        Trinket(
            'Half of a floorplan for a temple, '
            'castle, or some other structure'
        ),
        Trinket(
            'Bit of folded cloth that, when unfolded, turns into a stylish cap'
        ),
        Trinket('Receipt of deposit at a bank in a far-flung city'),
        Trinket('Diary with seven missing pages'),
        Trinket(
            'Empty silver snuffbox bearing an inscription '
            'the surface that says "dreams"'
        ),
        Trinket('Iron holy symbol devoted to an unknown god'),
        Trinket(
            'Book that tells the story of a legendary hero\'s rise and fall, '
            'with the last chapter missing'
        ),
        Trinket('Vial of dragon blood'),
        Trinket('Ancient arrow of elven design'),
        Trinket('Needle that never bends'),
        Trinket('Ornate brooch of dwarven design'),
        Trinket(
            'Empty wine bottle bearing a pretty label that says "The '
            'Wizard of Wines Winery, Red Dragon Crush, 331422-W"'
        ),
        Trinket('A mosaic tile with a multicolored, glazed surface'),
        Trinket('Petrified mouse'),
        Trinket(
            'Black pirate flag adorned with a dragon\'s skull and crossbones'
        ),
        Trinket(
            'Tiny mechanical crab or spider that moves '
            'about when it\'s not being observed'),
        Trinket(
            'Glass jar containing lard with a label '
            'that reads "Griffon Grease"'
        ),
        Trinket(
            'Wooden box with a ceramic bottom that holds a living '
            'worm with a head on each end of its body'
        ),
        Trinket('Metal urn containing the ashes of a hero'),
    ]
    number = randint(1, len(trinkets)) - 1

    print(f'You won a trinket: {trinkets[number].name}')
    print('Press ENTER to continue')
    input()

    return trinkets[number]


def get_variant(variant_name):
    """
    The function gets if the user selected to use the variant instead of the
    default version of its background.
    :param variant_name: Name of the possible variant in the user's background
    :return: boolean, if the user chosen or not the variant
    """
    variant = None

    if variant_name:
        prompt = f"There's the variant {variant_name.title()} for your class!"

        answer = select(
            options=['YES', 'NO'],
            prompt=prompt,
            single_item=True,
            go_back=False,
            finish=False,
        )
        if answer == 'YES':
            variant = True
        else:
            variant = False
    else:
        print('It appears that your class has no variant option.')

    clear_terminal()

    return variant


def deal_other_options(characteristic, characteristic_list):
    """
    If the user selected to randomize its background characteristics or to
    write its own version of it.
    :param characteristic: chosen characteristic by the user
    :param characteristic_list: list of all possible pre-chosen characteristics
    :return: the proper characteristic, be a random version or the write in.
    """
    if characteristic == 'RANDOM':
        characteristic = characteristic_list[
            randint(0, len(characteristic_list) - 1)
        ]
    elif characteristic == 'WRITE IN':
        characteristic = input('Write what you want: ')

    return characteristic


def select_level():
    answer = select(
        options=['WRITE LEVEL'],
        prompt='It is time to select your initial level.',
        single_item=True
    )

    if answer == 'WRITE LEVEL':
        level = None
        loop = True

        while loop:
            level = get_a_number(
                prompt='What is your initial level?',
                go_back_message=False
            )

            if level is None:
                print('\nYour level must be a number.')
                print('Press ENTER to continue...')
                input()
                clear_terminal()
            else:
                if level < 1 or level > 20:
                    print('\nPlease insert a number between 1 and 20.')
                    print('Press ENTER to continue...')
                    input()
                else:
                    loop = False

            clear_terminal()
    else:
        level = answer

    return level


def create_class(classe, level, abilities):
    """
    This function gets all the necessary info to create an object of the class
    Class and create it for the user.
    :param classe: string with the name of the chosen class
    :param level: int of the level number selected
    :param abilities: Abilities object with the abilities of the user
    :return: object of the class Class
    """

    if classe == 'BARBARIAN':
        equipment_options = [
            [
                index['EQUIPMENT']['WEAPON']['MARTIAL']['MELEE']
            ],
            [
                (
                    handaxe,
                    handaxe
                ),
                [
                    index['EQUIPMENT']['WEAPON']['SIMPLE']
                ]
            ],
        ]
        chosen_equipment = [
            packs['EXPLORER'],
            javelin,
            javelin,
            javelin,
            javelin
        ]

        classe = Barbarian(
            level=level,
            equipment_options=equipment_options,
            equipment=chosen_equipment,
        )
    elif classe == 'BARD':
        equipment_options = [
            [
                rapier,
                longsword,
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                tuple(packs['DIPLOMAT']),
                tuple(packs['ENTERTAINER'])
            ],
            [
                index['EQUIPMENT']['TOOLS']['MUSICAL INSTRUMENT']
            ],
        ]

        classe = Bard(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[leather_armor, dagger],
        )
    elif classe == 'CLERIC':
        equipment_options = [
            [
                mace,
                warhammer
            ],
            [
                scale_mail_armor,
                leather_armor,
                chain_mail_armor
            ],
            [
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                tuple(packs['PRIEST']),
                tuple(packs['EXPLORER'])
            ],
            [
                index['EQUIPMENT']['ADVENTURING GEAR']['HOLY SYMBOL']
            ]
        ]

        classe = Cleric(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[shield],
        )
    elif classe == 'DRUID':
        equipment_options = [
            [
                shield,
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                scimitar,
                index['EQUIPMENT']['WEAPON']['SIMPLE']['MELEE']
            ],
            [
                index['EQUIPMENT']['ADVENTURING GEAR']['DRUIDIC FOCUS']
            ]
        ]

        classe = Druid(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[leather_armor, packs['EXPLORER']],
        )
    elif classe == 'FIGHTER':
        equipment_options = [
            [
                [
                    chain_mail_armor
                ],
                (
                    leather_armor,
                    longbow
                )
            ],
            [
                index['EQUIPMENT']['WEAPON']['MARTIAL']
            ],
            [
                shield,
                index['EQUIPMENT']['WEAPON']['MARTIAL'],
            ],
            [
                (
                    handaxe,
                    handaxe
                ),
                [
                    light_crossbow
                ]
            ],
            [
                tuple(packs['DUNGEONEER']),
                tuple(packs['EXPLORER'])
            ]
        ]

        classe = Fighter(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
        )
    elif classe == 'MONK':
        equipment_options = [
            [
                shortsword,
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                tuple(packs['DUNGEONEER']),
                tuple(packs['EXPLORER'])
            ],
        ]
        chosen_equipment = [
            dart, dart, dart, dart, dart, dart, dart, dart, dart, dart
        ]

        classe = Monk(
            level=level,
            equipment_options=equipment_options,
            equipment=chosen_equipment,
        )
    elif classe == 'PALADIN':
        equipment_options = [
            [
                index['EQUIPMENT']['WEAPON']['MARTIAL']
            ],
            [
                shield,
                index['EQUIPMENT']['WEAPON']['MARTIAL']
            ],
            [
                (
                    javelin,
                    javelin,
                    javelin,
                    javelin,
                    javelin
                ),
                [
                    index['EQUIPMENT']['WEAPON']['SIMPLE']['MELEE']
                ]
            ],
            [
                tuple(packs['PRIEST']),
                tuple(packs['EXPLORER'])
            ],
            [
                index['EQUIPMENT']['ADVENTURING GEAR']['HOLY SYMBOL']
            ]
        ]

        classe = Paladin(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[chain_mail_armor],
        )
    elif classe == 'RANGER':
        print('Choose two simple melee weapons to be offered to you later:')
        equipment_options = [
            [
                scale_mail_armor,
                leather_armor
            ],
            [
                (
                    shortsword,
                    shortsword
                ),
                (
                    choose_equipment(
                        [[index['EQUIPMENT']['WEAPON']['SIMPLE']['MELEE']]]
                    )[0],
                    choose_equipment(
                        [[index['EQUIPMENT']['WEAPON']['SIMPLE']['MELEE']]]
                    )[0],
                )
            ],
            [
                tuple(packs['DUNGEONEER']),
                tuple(packs['EXPLORER'])
            ],
        ]

        classe = Ranger(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[longbow],
        )
    elif classe == 'ROGUE':
        equipment_options = [
            [
                rapier,
                shortsword
            ],
            [
                shortbow,
                shortsword
            ],
            [
                tuple(packs['BURGLAR']),
                tuple(packs['DUNGEONEER']),
                tuple(packs['EXPLORER'])
            ],
        ]
        chosen_equipment = [
            leather_armor,
            dagger,
            dagger,
            thieves_kit
        ]

        classe = Rogue(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=chosen_equipment,
        )
    elif classe == 'SORCERER':
        equipment_options = [
            [
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                component_pouch,
                index['EQUIPMENT']['ADVENTURING GEAR']['ARCANE FOCUS']
            ],
            [
                tuple(packs['DUNGEONEER']),
                tuple(packs['EXPLORER'])
            ],
        ]

        classe = Sorcerer(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[dagger, dagger],
        )
    elif classe == 'WARLOCK':
        equipment_options = [
            [
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
            [
                component_pouch,
                index['EQUIPMENT']['ADVENTURING GEAR']['ARCANE FOCUS']
            ],
            [
                tuple(packs['SCHOLAR']),
                tuple(packs['DUNGEONEER'])
            ],
            [
                index['EQUIPMENT']['WEAPON']['SIMPLE']
            ],
        ]

        classe = Warlock(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[leather_armor, dagger, dagger],
        )
    elif classe == 'WIZARD':
        equipment_options = [
            [
                quarterstaff,
                dagger
            ],
            [
                component_pouch,
                index['EQUIPMENT']['ADVENTURING GEAR']['ARCANE FOCUS']
            ],
            [
                tuple(packs['SCHOLAR']),
                tuple(packs['EXPLORER'])
            ],
        ]

        classe = Wizard(
            abilities=abilities,
            level=level,
            equipment_options=equipment_options,
            equipment=[spellbook],
        )

    classe.features = create_simple_list(classe.features)

    return classe


def print_abilities(character):
    print(
        f'Abilities:    '
        f'STR        '
        f'DEX        '
        f'CON        '
        f'INT        '
        f'WIS        '
        f'CHA        '
    )
    print(
        f'              '
        f"{character.abilities.values['STR']:02d} "
        f"({character.abilities.score('STR'):+})    "
        f"{character.abilities.values['DEX']:02d} "
        f"({character.abilities.score('DEX'):+})    "
        f"{character.abilities.values['CON']:02d} "
        f"({character.abilities.score('CON'):+})    "
        f"{character.abilities.values['INT']:02d} "
        f"({character.abilities.score('INT'):+})    "
        f"{character.abilities.values['WIS']:02d} "
        f"({character.abilities.score('WIS'):+})    "
        f"{character.abilities.values['CHA']:02d} "
        f"({character.abilities.score('CHA'):+})    "
    )


def print_main_info(character):
    headline = '\nLevel ' \
               + 'Proficiency   ' \
               + 'AC  ' \
               + 'HP   ' \
               + 'Speed  ' \
               + 'Alignment        ' \
               + 'Initiative  ' \
               + 'Background'

    values = f'{character.general_info["LEVEL"]:02d}         ' \
             + f'{character.proficiencies["VALUE"]:02d}       ' \
             + f'{character.general_stats["AC"]}  ' \
             + f'{character.general_stats["CURRENT HP"]:03d}  ' \
             + f'{character.general_stats["SPEED"]}     ' \
             + f'{character.general_info["ALIGNMENT"].title():15s}  ' \
             + f'{character.general_stats["INITIATIVE"]}           ' \
             + f'{character.general_info["BACKGROUND"].title()}'

    print(headline)
    print(values)


# TODO: Limit characters showing physical appearance
#       (keywords: PHYSICAL APPEARANCE)


def show_character_info(character):
    clear_terminal()
    print_name(
        name=character.personal_info["CHARACTER'S NAME"].title(),
        category=f'{character.general_info["RACE"].title()} '
                 + f'{character.general_info["CLASS"].title()}'
    )
    print_abilities(character)
    print_main_info(character)
    print('')


def select_cantrips(character):
    cantrips_to_select = character.magical_ability.cantrips_known \
                         - len(character.magical_ability.cantrips)
    possible_cantrips = index['CANTRIPS'][character.general_info['CLASS']]. \
        copy()

    for cantrip in character.magical_ability.cantrips:
        possible_cantrips.remove(cantrip)

    clear_terminal()
    print(
        f'As a {character.general_info["CLASS"]}, you have '
        f'{cantrips_to_select}  cantrips to select:\n'
    )

    cantrips = select(
        options=possible_cantrips,
        quantity=cantrips_to_select,
        prompt='You have cantrips to select.',
    )

    return cantrips


def select_spells(character):
    added_spells = []
    for level, spells in character.magical_ability.spells.items():
        added_spells += spells

    spells_to_select = character.magical_ability.spells_known - len(
        added_spells)

    all_spells = {}
    class_spells_by_level = index['SPELLS'][character.general_info['CLASS']]

    max_spell_slot = None
    for level, slots in character.magical_ability.spell_slots.items():
        if slots > 0:
            max_spell_slot = level

    for level, spells in class_spells_by_level.items():
        if level <= max_spell_slot:
            for spell in spells:
                if spell not in added_spells:
                    all_spells[spell] = level

    clear_terminal()
    print(
        f'As a {character.general_info["CLASS"]}, you have '
        f'{spells_to_select} spells up to level {max_spell_slot} to select:\n'
    )
    all_spells_list = list(all_spells.keys())
    spells_list = select(
        options=all_spells_list,
        quantity=spells_to_select,
        prompt='You have spells to select.',
    )

    if spells_list not in [['EXIT'], ['GO BACK']]:
        spells = {}
        for level in range(1, max_spell_slot + 1):
            if level not in spells:
                spells[level] = []

        spells_list += added_spells
        for spell in spells_list:
            spells[all_spells[spell]].append(spell)
    else:
        spells = spells_list[0]

    return spells


def get_dict_with_units(original):
    return_dict = {}

    for equipment in original:
        if equipment in return_dict:
            return_dict[equipment] += 1
        else:
            return_dict[equipment] = 1

    return return_dict


def show_character(character):
    end = False

    while not end:
        show_character_info(character)

        what_to_see = [
            'SAVING THROWS',
            'SKILLS',
            'LANGUAGES',
            'PROFICIENCY IN EQUIPMENTS',
            'EQUIPMENT',
            'FEATURES',
            'PERSONAL INFO',
            'SPELLS',
        ]

        answer = select(
            options=what_to_see,
            single_item=True,
            clean=False,
            finish=False,
        )

        if answer == 'SAVING THROWS':
            show_character_info(character)

            for ability in index['ABILITIES']:
                total = character.abilities.score(ability)
                if ability in character.proficiencies["SAVING THROWS"]:
                    saving_throw = f'+ {character.proficiencies["VALUE"]} '
                    total += character.proficiencies["VALUE"]
                else:
                    saving_throw = '    '

                print(
                    f'{ability.title()}: '
                    f'{character.abilities.score(ability):02d} '
                    f'{saving_throw} '
                    f'= {total:02d}'
                )

            print("\nPress ENTER to continue")
            input()

        elif answer == 'SKILLS':
            show_character_info(character)

            for skill, ability in index['SKILLS'].items():
                total = character.abilities.score(ability)

                if skill in character.proficiencies["SKILLS"]:
                    proficiency = f'+ {character.proficiencies["VALUE"]} '
                    total += character.proficiencies["VALUE"]
                else:
                    proficiency = '    '

                name = f'{skill.title()} ({ability})'

                print(
                    f'{name:25s}: '
                    f'{character.abilities.score(ability):02d} '
                    f'{proficiency}'
                    f'= {total:3d}'
                )

            print('\nPress ENTER to continue')
            input()

        elif answer == 'LANGUAGES':
            show_character_info(character)

            character.languages = create_simple_list(character.languages)

            print('Languages spoken:')
            for language in character.languages:
                print(f'- {language.title()};')

            print('\nPress ENTER to continue')
            input()

        elif answer == 'PROFICIENCY IN EQUIPMENTS':
            show_character_info(character)
            print('You have proficiency in the following equipment:')

            print('\nArmors:')
            if len(character.proficiencies["ARMORS"]) == 0:
                print('- No armor.')
            else:
                for armor in character.proficiencies["ARMORS"]:
                    print(f'- {armor.title()}')

            print('\nWeapons:')
            if len(character.proficiencies["WEAPONS"]) == 0:
                print('- No weapon.')
            else:
                for weapon in character.proficiencies["WEAPONS"]:
                    print(f'- {weapon.title()}')

            print('\nTools:')
            if len(character.proficiencies["TOOLS"]) == 0:
                print('- No tool.')
            else:
                for tool in character.proficiencies["TOOLS"]:
                    print(f'- {tool.title()}')

            print('\nPress ENTER to continue')
            input()

        elif answer == 'EQUIPMENT':
            armors = get_dict_with_units(character.equipments['ARMORS'])
            weapons = get_dict_with_units(character.equipments['WEAPONS'])
            gears = get_dict_with_units(character.equipments[
                                            'ADVENTURING GEARS'])
            tools = get_dict_with_units(character.equipments['TOOLS'])
            mounts = get_dict_with_units(character.equipments[
                                             'MOUNTS AND VEHICLES'])
            trinkets = get_dict_with_units(character.equipments['TRINKETS'])

            show_character_info(character)

            if armors:
                print_name('Armors')
                print(
                    'Name               Armor Class    Weight    '
                    + 'Dex Max     Strength          Units'
                )
                for armor, units in armors.items():
                    if armor.strength is False:
                        strength = str(0)
                    else:
                        strength = str(armor.strength)

                    if armor.dex_max is False:
                        dex_max = str(armor.dex_max)
                    else:
                        dex_max = f'  {armor.dex_max}  '

                    print(
                        f'{armor.name.title():24s}'
                        f'{str(armor.armor_class):12s}'
                        f'{str(armor.weight):10s}'
                        f'{dex_max:13s}'
                        f'{strength:17s}'
                        f'{units}'
                    )
                print('\n')

            if weapons:
                print_name('Weapons')
                print(
                    'Name              Damage    '
                    'Damage Type                   Weight          Units'
                )
                for weapon, units in weapons.items():
                    name = f'{weapon.name.title():19s}'
                    damage = f'{convert_dice_to_d_format(weapon.damage):9s}'
                    damage_type = f'{weapon.damage_type:30s}'
                    weight = f'{weapon.weight} lb.'
                    weight = f'{weight:18s}'
                    print(name + damage + damage_type + weight + str(units))
                print('\n')

            if gears:
                print_name('Adventuring Gears')
                print('Name' + ' ' * 50 + 'Weight (lb.)' + ' ' * 8 + 'Units')
                for gear, units in gears.items():
                    print(
                        f'{gear.name.title():59s}'
                        f'{str(gear.weight):17s}'
                        f'{units}'
                    )
                print('\n')

            if tools:
                print_name('Tools')
                print('Name' + ' ' * 50 + 'Weight (lb.)' + ' ' * 8 + 'Units')
                for tool, units in tools.items():
                    print(
                        f'{tool.name.title():59s}'
                        f'{str(tool.weight):17s}'
                        f'{units}'
                    )
                print('\n')

            if mounts:
                print_name('Mounts and Vehicles')
                for mount in mounts:
                    print(f'- {mount.name.title()}')

            if trinkets:
                print_name('Trinkets')
                for trinket in trinkets:
                    print(f'- {trinket.name.title()}')

            print_name('WEIGHT')
            print(f'Total weight carried: {character.equipments["WEIGHT"]}')
            if character.equipments['WEIGHT'] \
                    > character.abilities.values['STR'] * 15:
                print('You are carrying way too much. Keep it easy, man!')
            else:
                print('You are carrying just fine!')
            print('')

            print_name()
            print('Press ENTER to continue')
            input()

        elif answer == 'FEATURES':
            show_character_info(character)

            print_name('Racial Features')
            if character.features['RACE']:
                for feature in character.features['RACE']:
                    print(f'- {feature.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print_name('Class Features')
            if character.features['CLASS']:
                for feature in character.features["CLASS"]:
                    print(f'- {feature.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print_name('Background Feature')
            if character.features['BACKGROUND']:
                for feature in character.features["BACKGROUND"]:
                    print(f'- {feature.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print_name('Advantages')
            if character.features['ADVANTAGES']:
                for advantage in character.features['ADVANTAGES']:
                    print(f'- {advantage.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print_name('Disadvantages')
            if character.features['DISADVANTAGES']:
                for disadvantages in character.features['DISADVANTAGES']:
                    print(f'- {disadvantages.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print_name('Resistances')
            if character.features['RESISTANCES']:
                for resistance in character.features['RESISTANCES']:
                    print(f'- {resistance.title()}')
            else:
                print('Nothing to show here!')
            print('\n')

            print('Press ENTER to continue.')
            input()

        elif answer == 'PERSONAL INFO':
            show_character_info(character)

            print_name('Physical appearance')
            print(
                'Age      Eye Color      Skin Color      '
                'Hair Color      Height      Weight'
            )
            print(
                f'{character.personal_info["AGE"].strip().split(" ")[0]:9s}'
                f'{character.personal_info["EYE"]:15s}'
                f'{character.personal_info["SKIN"]:16s}'
                f'{character.personal_info["HAIR"]:16s}'
                f'{character.personal_info["HEIGHT"]:12s}'
                f'{character.personal_info["WEIGHT"]}'
                f'\n'
            )

            backgrounds_speciality = {
                'CHARLATAN': 'FAVORITE SCHEME',
                'CRIMINAL': 'CRIMINAL SPECIALITY',
                'SPY': 'CRIMINAL SPECIALITY',
                'ENTERTAINER': 'ENTERTAINER ROUTINES',
                'GLADIATOR': 'ENTERTAINER ROUTINES',
                'FOLK HERO': 'DEFINING EVENT',
                'GUILD ARTISAN': 'GUILD BUSINESS',
                'GUILD MERCHANT': 'GUILD BUSINESS',
                'HERMIT': 'LIFE OF SECLUSION',
                'OUTLANDER': 'ORIGIN',
                'SAGE': 'SPECIALTY',
                'SOLDIER': 'SPECIALTY',
            }

            print_name("Psychological traits")
            if character.general_info['BACKGROUND'] in backgrounds_speciality:
                background_speciality = \
                    backgrounds_speciality[character.general_info['BACKGROUND']]

                print(
                    f'{background_speciality.title()}: '
                    f'{character.psychology["BACKGROUND SPECIALITY"]}'
                    f'\n'
                )

            print(
                f'Personality trait: '
                f'{character.psychology["PERSONALITY TRAIT"]}\n'
            )
            print(f'Ideal: {character.psychology["IDEAL"]}\n')
            print(f'Bond: {character.psychology["BOND"]}\n')
            print(f'Flaw: {character.psychology["FLAW"]}\n')

            print_name('History')
            print('')
            for line in character.personal_info['HISTORY']:
                print(line)

            print('')
            print('Press ENTER to continue')
            input()

        elif answer == 'SPELLS':
            if character.magical_ability.has_magic:
                go_on = True
                if len(character.magical_ability.cantrips) \
                        < character.magical_ability.cantrips_known:
                    new_cantrips = select_cantrips(character)

                    if new_cantrips not in ['EXIT', 'GO BACK']:
                        character.magical_ability.set_cantrips(new_cantrips)
                        save_sheet(character)
                    elif new_cantrips == 'EXIT':
                        go_on = False
                elif character.magical_ability.cantrips_known == -1:
                    character.magical_ability.set_cantrips([])

                if go_on:
                    spells_list = []
                    for level, level_spells in character.magical_ability.spells \
                            .items():
                        spells_list += level_spells

                    if len(spells_list) \
                            < character.magical_ability.spells_known:
                        new_spells = select_spells(character)

                        if new_spells not in ['EXIT', 'GO BACK']:
                            character.magical_ability.set_spells(new_spells)
                            save_sheet(character)
                        elif new_spells == 'EXIT':
                            return 'EXIT'

                    show_character_info(character)
                    print_name('Cantrips')
                    print('')
                    if len(character.magical_ability.cantrips) < 1:
                        print('No cantrip to show here!')
                    else:
                        for cantrip in character.magical_ability.cantrips:
                            print(f'- {cantrip.title()}')
                    print('')

                    if len(character.magical_ability.spells) > 0:
                        for level, spells in character.magical_ability.spells. \
                                items():
                            if level == 1:
                                ordinal = 'st'
                            elif level == 2:
                                ordinal = 'nd'
                            elif level == 3:
                                ordinal = 'rd'
                            else:
                                ordinal = 'th'

                            print_name(f'{level}{ordinal} level spells')
                            print('')
                            for spell in spells:
                                print(f'- {spell.title()}')
                            print('')
                    elif character.magical_ability.spells_known == -1:
                        for level, spells in index['SPELLS'][
                            character.general_info['CLASS']].items():
                            if level == 1:
                                ordinal = 'st'
                            elif level == 2:
                                ordinal = 'nd'
                            elif level == 3:
                                ordinal = 'rd'
                            else:
                                ordinal = 'th'

                            print_name(f'{level}{ordinal} level spells')
                            print('')
                            for spell in spells:
                                print(f'- {spell.title()}')
                            print('')

                    for level in range(
                            len(character.magical_ability.spells) + 1,
                            character.magical_ability.highest_spell_level + 1):
                        if level == 1:
                            ordinal = 'st'
                        elif level == 2:
                            ordinal = 'nd'
                        elif level == 3:
                            ordinal = 'rd'
                        else:
                            ordinal = 'th'

                        print_name(f'{level}{ordinal} level spells')
                        print('')
                        print('No spell to show here!')
                        print('')

                    print('')
                    print('Press ENTER to continue')
                    input()
            else:
                show_character_info(character)
                print('It appears that your character has no coward magic!')
                print('Go out there and smash their heads!')
                print('Press ENTER to continue')
                input()

        elif answer == 'GO BACK':
            end = True

        clear_terminal()


def get_history():
    print("What is your character's history?")

    history = []
    new_paragraph = None
    while new_paragraph != '':
        new_paragraph = input()
        history.append(new_paragraph)

    return history[:-1]


def get_player_name():
    name = input('What is your name? ')
    clear_terminal()

    return name


def get_name():
    confirmed = False
    name = ''

    while not confirmed:
        name = input("What is your character's name? ")

        print(f'\nYou typed: {name}.')

        valid_answer = False
        while not valid_answer:
            confirmation = input('Do you confirm it? YES or NO? ')
            confirmation = confirmation.upper()

            if confirmation == 'YES' or confirmation == 'Y':
                valid_answer = True
                confirmed = True
            elif confirmation == 'NO' or confirmation == 'N':
                valid_answer = True
            else:
                print('\nPlease, type only YES or NO')

            clear_terminal()

    return name


def get_age(race):
    prompt = \
        f"Typically, a {race.name} has between {race.age[0]} and " \
        f"{race.age[1]} years old in the adult phase.\n" \
        "What is your character's age?"
    age = get_a_number(prompt=prompt, go_back_message=False)
    age = str(age)

    return age


def get_height(race):
    text = f'Typically, a {race.name} has between {race.height[0]}\' and ' \
           f'{race.height[1]}\' of height.\n' \
           f'What is your character\'s height?'
    height = get_a_number(prompt=text, go_back_message=False)
    height = str(height)

    return height


def get_weight():
    weight = get_a_number(
        prompt="What is your character's weight?",
        go_back_message=False
    )
    weight = str(weight)

    return weight


def get_eye_color():
    eye = get_a_number(
        prompt="What is your character's eye color?",
        go_back_message=False
    )
    eye = str(eye)

    return eye


def get_skin_color():
    skin = get_a_number(
        prompt="What is your character's skin color?",
        go_back_message=False
    )
    skin = str(skin)

    return skin


def get_hair_color():
    hair = get_a_number(
        prompt="What is your character's hair color?",
        go_back_message=False
    )
    hair = str(hair)

    return hair


def get_personal_info(race):
    """
    Asks for the user irrelevant data about the character
    :return: Dict with all data gathered in the function
    """
    player_name = get_player_name()
    character_name = get_name()
    age = get_age(race)
    height = get_height(race)
    weight = get_weight()
    eyes_color = get_eye_color()
    skin_color = get_skin_color()
    hair_color = get_hair_color()
    history = get_history()

    personal_info = {
        "PLAYER'S NAME": player_name,
        "CHARACTER'S NAME": character_name,
        "AGE": age,
        "HEIGHT": height,
        "WEIGHT": weight,
        "EYE": eyes_color,
        "SKIN": skin_color,
        "HAIR": hair_color,
        "HISTORY": history
    }

    return personal_info


def generate_random_values():
    """
    Generates the random values of the abilities and asks for the player
    to which places they shall be assigned
    :return: list: all the random values
    """
    die = Dice(1, 6)  # Creates a d6

    def correct_values(values):
        """
        Checks the values for the conditions that states them as correct
        :param values: The list with the 6 values generated randomly
        :return: bool: If the values are correct or not
        """
        if not values:
            return False
        else:
            modifiers = []  # A list with all the modifiers from the abilities
            biggest_value = 0

            for number in values:
                modifier = floor((number - 10) / 2)
                modifiers.append(modifier)

                if number > biggest_value:
                    biggest_value = number

            # If there isn't a single value over 13, the values must be redone
            if biggest_value < 14:
                return False
            # If the sum of modifiers is negative, the values must be redone
            elif sum(modifiers) < 3:
                return False
            # If the sum modifiers is too big, the values must be redone
            elif sum(modifiers) > 9:
                return False
            else:
                return True

    scores = []
    while not correct_values(scores):
        scores = []

        for _ in range(1, 7):
            dice = []

            for _ in range(1, 5):
                # Roll the dice to generate the random value from 1 to 6
                value = die.roll(0)
                dice.append(value)

            # Removes from the list the die with the lesser value
            dice.sort()
            dice.pop(0)

            scores.append(sum(dice))  # Store the sum of the 3 dice

    return scores


def show_major_abilities(classe):
    """
    Every class has its most important abilities. This function prints the ones
    listed in the Player's Handbook, so the user do a better choice.
    :param classe: String representing the class chosen by user
    """
    abilities = []

    if isinstance(classe, Class):
        classe = classe.name

    if classe == 'BARBARIAN':
        abilities = [['STR'], ['CON']]
    elif classe == 'BARD':
        abilities = [['CHA'], ['DEX']]
    elif classe == 'CLERIC':
        abilities = [['WIS'], ['STR', 'CON']]
    elif classe == 'DRUID':
        abilities = [['WIS'], ['CON']]
    elif classe == 'FIGHTER':
        abilities = [['STR', 'DEX'], ['CON', 'INT']]
    elif classe == 'MONK':
        abilities = [['DEX'], ['WIS']]
    elif classe == 'PALADIN':
        abilities = [['STR'], ['CHA']]
    elif classe == 'RANGER':
        abilities = [['DEX'], ['WIS']]
    elif classe == 'ROGUE':
        abilities = [['DEX'], ['INT', 'CHA']]
    elif classe == 'SORCERER':
        abilities = [['CHA'], ['CON']]
    elif classe == 'WARLOCK':
        abilities = [['CHA'], ['CON']]
    elif classe == 'WIZARD':
        abilities = [['INT'], ['CON', 'DEX', 'CHA']]

    print(f'For major ability, the recommendation is/are:')
    for ability in abilities[0]:
        print(f'- {ability}')
    print('')

    print(f'For the second major ability, the recommendation is/are:')
    for ability in abilities[1]:
        print(f'- {ability}')
    print('')


def get_abilities_values(values, classe):
    """
    Allows the user to assign the desired values of its abilities.
    :param values: A list of the values generated for the user.
    :param classe: String with the name of the class selected by the user
    :return: Dictionary containing the values sorted by the user
    """

    abilities = {
        'STR': 'Strength',
        'DEX': 'Dexterity',
        'CON': 'Constitution',
        'INT': 'Intelligence',
        'WIS': 'Wisdom',
        'CHA': 'Charisma'
    }
    new_values = {}

    for ability_short, ability_name in abilities.items():
        end = False
        while not end:
            print(f'Your abilities scores are: {values}')
            print('Choose wisely!\n')

            show_major_abilities(classe)

            if new_values:
                for ability, value in new_values.items():
                    print(
                        f'Insert the value of {abilities[ability].title()}: '
                        f'{value}'
                    )

            value = input(f'Insert the value of {ability_name.title()}: ')
            if value.isnumeric():
                value = int(value)

                if value in values:
                    values.remove(value)
                    new_values[ability_short] = value
                    end = True
                else:
                    clear_terminal()
                    print(
                        'This value is not in your random values. '
                        'Please try again'
                    )
            else:
                clear_terminal()
                print(
                    "Your answer doesn't look like a number. "
                    'Please try again'
                )

        clear_terminal()

    return new_values


def buy_points(classe):
    clear_terminal()

    total_points = 27
    points_spent = 0
    values = {
        'STR': 8,
        'DEX': 8,
        'CON': 8,
        'INT': 8,
        'WIS': 8,
        'CHA': 8
    }

    confirmed = False
    while not confirmed:
        left_points = total_points - points_spent

        options = {
            f'Strength: {values["STR"]}': 'STR',
            f'Dexterity: {values["DEX"]}': 'DEX',
            f'Constitution: {values["CON"]}': 'CON',
            f'Intelligence: {values["INT"]}': 'INT',
            f'Wisdom: {values["WIS"]}': 'WIS',
            f'Charisma: {values["CHA"]}': 'CHA',
            f'Confirm values': 'CONFIRM'
        }

        show_major_abilities(classe)
        ability = select(
            options=options,
            prompt=f'You have {left_points} points to spend.',
            show_type='key',
            return_type='value',
            clean=False,
            single_item=True,
            go_back=False,
            finish=False,
        )

        if ability != 'CONFIRM':
            print('')
            print('Ability score point cost')

            point_cost = {
                8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
            }
            scores = ''
            costs = ''

            for point, cost in point_cost.items():
                scores += f'{str(point):10s}'
                costs += f'{str(cost):10s}'

            print('')
            print(scores)
            print(costs)
            print('')

            old_value = values[ability]
            new_value = input(f'Type the new {ability.title()} value: ')
            if not new_value.isnumeric:
                print('\nValue must be a number.')
                print('Press ENTER and try again.')
                input()
            elif int(new_value) not in point_cost:
                print('\nValue not found in the table.')
                print('Press ENTER and try again.')
                input()
            else:
                new_value = int(new_value)
                if points_spent \
                        - point_cost[old_value] \
                        + point_cost[new_value] \
                        < 0:
                    print('You don\'t have the points to buy this value.')
                    print('Press ENTER and try again.')
                    input()
                else:
                    points_spent -= point_cost[old_value]
                    points_spent += point_cost[new_value]
                    values[ability] = new_value
        else:
            confirmed = True

        clear_terminal()

    return values


def get_existing_abilities_values(abilities, ability_increase):
    values = []
    for ability, value in abilities.values.items():
        if ability in ability_increase:
            values.append(
                value - ability_increase[ability]
            )
        else:
            values.append(value)

    return values


def create_abilities(classe, race, abilities=None):
    clear_terminal()

    if abilities is None:
        options = [
            'GENERATE RANDOM VALUES',
            'USE DEFAULT VALUES',
            'BUY ABILITIES POINTS'
        ]

        answer = select(
            options=options,
            prompt='There are three different ways to '
                   'generate the values of your character',
            single_item=True,
        )
        clear_terminal()
    else:
        options = ['DISTRIBUTE AGAIN', 'USE IT IN THE SAME WAY']
        answer = select(
            options=options,
            prompt='You already generated values for this character. Select'
                   'what you want to do with them now.',
            single_item=True
        )
        clear_terminal()

    if answer == 'GO BACK' or answer == 'EXIT':
        return answer
    else:
        if answer == 'BUY ABILITIES POINTS':
            values = buy_points(classe)
        else:
            values = None
            if abilities:
                values = get_existing_abilities_values(
                    abilities, race.ability_increase)
            elif answer == 'GENERATE RANDOM VALUES':
                values = generate_random_values()
            elif answer == 'USE DEFAULT VALUES':
                values = [15, 14, 13, 12, 10, 8]

            if answer != 'USE IT IN THE SAME WAY':
                values = get_abilities_values(values, classe)
            elif answer == 'USE IT IN THE SAME WAY':
                acronyms = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
                new_values = {}
                for i in range(6):
                    new_values[acronyms[i]] = values[i]
                values = new_values

        abilities = Abilities(
            values['STR'],
            values['DEX'],
            values['CON'],
            values['INT'],
            values['WIS'],
            values['CHA']
        )

        if 'TWO ABILITIES INCREASE' in race.features:
            abilities_options = index['ABILITIES'].copy()
            abilities_options.pop('CHA')

            abilities_to_increase = select(
                options=abilities_options,
                quantity=2,
                prompt=f'As a {race.name}, you can choose the abilities in '
                       'which you has increment in the value.',
                show_type='value',
                return_type='key',
                go_back=False,
                finish=False,
            )

            for ability in abilities_to_increase:
                race.ability_increase[ability] = 1

        for ability, increase in race.ability_increase.items():
            abilities.increment_ability(ability=ability, value=increase)

        return abilities


def choose_or_bought():
    # The rules on equipment have variants, so the user can choose if he/she
    # wants to buy the equipment with a amount of money defined by its class or
    # to select it from the possible options given by the class and background
    answer = select(
        options=['BUY', 'CHOOSE'],
        prompt='You may BUY or CHOOSE your equipment, what would you like?',
        single_item=True,
    )

    if answer == 'BUY':
        equipment_bought = True
    elif answer == 'CHOOSE':
        equipment_bought = False
    else:
        equipment_bought = answer

    clear_terminal()

    return equipment_bought


def unite_proficiency(*proficiency):
    final_list = []
    for a_list in proficiency:
        for element in a_list:
            element_value = find_in_dict(element, index)
            if element_value is not None:
                if isinstance(element_value, list) \
                        or isinstance(element_value, dict) \
                        or isinstance(element_value, tuple):
                    new_list = create_simple_list(element_value)
                else:
                    new_list = [element_value]

                for item in new_list:
                    if item.name not in final_list:
                        final_list.append(item.name)

    return final_list


def race_magic(race_name, level, magical_ability):
    if race_name == 'DARK ELF':
        if 'DANCING LIGHTS' not in magical_ability.cantrips:
            magical_ability.cantrips.append('DANCING LIGHTS')

        if level >= 3:
            if 'FAERIC FIRE' not in magical_ability.spells:
                magical_ability.set_spells({1: 'FAERIC FIRE'})

            if level >= 5:
                if 'DARKNESS' not in magical_ability.spells:
                    magical_ability.set_spells({2: 'DARKNESS'})

    if race_name == 'TIEFLING':
        if 'THAUMATURGY' not in magical_ability.cantrips:
            magical_ability.set_cantrips('THAUMATURGY')

        if level >= 3:
            if 'HELLISH REBUKE' not in magical_ability.spells:
                magical_ability.set_spells({1: 'HELLISH REBUKE'})

            if level >= 5:
                if 'DARKNESS' not in magical_ability.spells:
                    magical_ability.set_spells({2: 'DARKNESS'})


def get_alignment():
    # Get alignment
    alignment = select(
        options=index['ALIGNMENTS'],
        prompt='In Dungeons and Dragons, there are 9 possible alignments.',
        single_item=True
    )
    clear_terminal()

    return alignment


def select_background():
    # Get background name
    background = select(
        options=index['BACKGROUNDS'] + ['GO BACK', 'EXIT'],
        prompt='In Dungeons and Dragons, there are 13 possible backgrounds.',
        single_item=True
    )
    clear_terminal()

    if background == 'ACOLYTE':
        chosen_equipment = [
            book, clothes['COSTUME'], clothes['COMMON'],
            pouch, incense, incense, incense, incense, incense
        ]

        background = Acolyte(
            equipment=chosen_equipment,
            equipment_options=[[holy_symbol]],
        )

    elif background == 'CHARLATAN':
        background = Charlatan(
            equipment=[clothes['COMMON'], disguise_kit, pouch],
            equipment_options=[[tools_of_the_con]],
        )

    elif background == 'CRIMINAL':
        background = Criminal(
            equipment=[crowbar, clothes['COMMON'], pouch],
            variant=get_variant('SPY'),
        )

    elif background == 'ENTERTAINER':
        equipments_options = [
            [
                index['EQUIPMENT']['TOOLS']['MUSICAL INSTRUMENT']
            ],
            [
                admirer_favor,
            ]
        ]
        background = Entertainer(
            equipment=[clothes['COSTUME'], pouch, guild_letter],
            equipment_options=equipments_options,
            variant=get_variant('GLADIATOR'),
        )

    elif background == 'FOLK HERO':
        chosen_equipment = [
            shovel, iron_pot, clothes['COMMON'],
            pouch, guild_letter, clothes['TRAVELER\'S']
        ]
        background = FolkHero(
            equipment=chosen_equipment,
            equipment_options=[[artisans_tools]],
        )

    elif background == 'GUILD ARTISAN':
        background = GuildArtisan(
            equipment=[clothes['TRAVELER\'S'], pouch],
            equipment_options=[[artisans_tools]],
            variant=get_variant('GUILD MERCHANT'),
        )

    elif background == 'HERMIT':
        chosen_equipment = [
            clothes['COMMON'],
            herbalism_kit,
            map_or_scroll_case,
            winter_blanket,
        ]
        background = Hermit(
            equipment=chosen_equipment,
        )

    elif background == 'NOBLE':
        variant = get_variant('KNIGHT')
        chosen_equipment = [
            clothes['FINE'], signet_ring, pouch, scroll_pedigree
        ]
        background = Noble(
            equipment=chosen_equipment,
            variant=variant,
        )

    elif background == 'OUTLANDER':
        chosen_equipment = [
            druidic_focus['WOODEN\'S STAFF'],
            hunting_trap,
            animal_trophy,
            clothes['TRAVELER\'S'],
            pouch
        ]
        background = Outlander(
            equipment=chosen_equipment,
        )

    elif background == 'SAGE':
        chosen_equipment = [
            ink, letter_from_colleague, clothes['COMMON'], pouch
        ]
        background = Sage(equipment=chosen_equipment)

    elif background == 'SAILOR':
        background = Sailor(
            equipment=[club, silk_rope, lucky_charm, clothes['COMMON'], pouch],
            variant=get_variant('PIRATE'),
        )

    elif background == 'SOLDIER':
        background = Soldier(
            equipment=[insignia_rank, enemy_trophy, clothes['COMMON'], pouch],
        )

    elif background == 'URCHIN':
        chosen_equipment = [
            small_knife, city_map, pet_mouse,
            parents_token, clothes['COMMON'], pouch
        ]
        background = Urchin(equipment=chosen_equipment)

    return background


def select_new_languages(background, race):
    new_languages = background.languages
    for feature in race.features:
        if feature == 'EXTRA LANGUAGE':
            new_languages += 1
            race.features.remove(feature)

    language_options = index['LANGUAGES'].copy()
    for language in race.languages:
        language_options.remove(language)

    new_languages = select(
        options=language_options,
        quantity=new_languages,
        prompt='You can choose new languages!'
    )
    clear_terminal()

    if new_languages not in ['EXIT', 'GO BACK']:
        languages = race.languages + new_languages
    else:
        languages = new_languages

    return languages


def select_proficient_tool(race, classe, background):
    cont = True
    tools = None
    race_tools = None
    class_tools = None

    if race.tools_options and cont:
        race_tools = select(
            options=race.tools_options,
            quantity=race.number_tools,
            prompt=f'As a {race.name}, choose the tools in which you are '
                   f'proficient with.'
        )

        cont = 'EXIT' not in race_tools and 'GO BACK' not in race_tools

        if not cont:
            if 'EXIT' in race_tools:
                tools = 'EXIT'
            else:
                tools = 'GO BACK'

    if classe.tools_options and cont:
        class_tools = select(
            options=classe.tools_options,
            quantity=classe.number_tools,
            prompt=f'As a {classe.name}, choose the tools in which you are '
                   f'proficient with.',
        )

        cont = 'EXIT' not in class_tools and 'GO BACK' not in class_tools

        if not cont:
            if 'EXIT' in tools:
                tools = 'EXIT'
            else:
                tools = 'GO BACK'

    if background.tools_options and cont:
        back_tools = select(
            options=background.tools_options,
            quantity=background.number_tools,
            prompt=f'As a {background.name}, choose the tools in which you are '
                   f'proficient with.',
        )

        cont = 'EXIT' not in back_tools and 'GO BACK' not in back_tools

        if not cont:
            if 'EXIT' in tools:
                tools = 'EXIT'
            else:
                tools = 'GO BACK'
        else:
            tools = {
                'RACE': race_tools,
                'CLASS': class_tools,
                'BACKGROUND': back_tools
            }

    return tools


def select_skills(
        race,
        classe,
        background
):
    cont = True
    all_skills = None
    classe_skills_proficiency = []
    if 'SKILL VERSATILITY' in race.features:
        race.skills_proficiency = []

    default_skills = race.skills_proficiency + background.skills
    skill_options = index['SKILLS'].copy()
    skill_options = list(skill_options.keys())

    for skill in default_skills:
        if skill in skill_options:
            skill_options.remove(skill)
        else:
            raise Exception('All skills in default skills must be in index!')

    if classe.possible_skills:
        skill_options = classe.possible_skills.copy()

        for skill in default_skills:
            if skill in skill_options:
                skill_options.remove(skill)

        new_skills = select(
            options=skill_options,
            quantity=classe.number_skills,
            prompt=f'As a {classe.name}, you can choose skills to be proficient'
        )

        cont = 'EXIT' not in new_skills and 'GO BACK' not in new_skills

        if cont:
            for skill in new_skills:
                skill_options.remove(skill)

            classe_skills_proficiency += new_skills
        elif 'EXIT' in new_skills:
            all_skills = 'EXIT'
        elif 'GO BACK' in new_skills:
            all_skills = 'GO BACK'

    if cont:
        if 'SKILL VERSATILITY' in race.features:
            new_skills = select(
                options=skill_options,
                quantity=2,
                prompt=f'As a {race.name}, you can choose the '
                       f'skills that you have proficiency.',
            )

            cont = 'EXIT' not in new_skills and 'GO BACK' not in new_skills
            if cont:
                race.skills_proficiency = new_skills
            elif 'EXIT' in new_skills:
                all_skills = 'EXIT'
            elif 'GO BACK' in new_skills:
                all_skills = 'GO BACK'

    if cont:
        classe.skills_proficiency = classe_skills_proficiency
        all_skills = race.skills_proficiency \
                     + classe.skills_proficiency \
                     + background.skills

    return all_skills


def group_equipment(equipments):
    if 'WEAPONS' not in equipments:
        weapons = []
        armors = []
        trinkets = []
        tools = []
        mounts = []
        gear = []
        total_weight = 0

        for equipment in equipments:
            if isinstance(equipment, Weapon):
                weapons.append(equipment)
            elif isinstance(equipment, Armor):
                armors.append(equipment)
            elif isinstance(equipment, Trinket):
                trinkets.append(equipment)
            elif isinstance(equipment, Tool):
                tools.append(equipment)
            elif isinstance(equipment, MountsAndVehicles):
                mounts.append(equipment)
            elif isinstance(equipment, AdventuringGear):
                gear.append(equipment)
            else:
                raise Exception('It appears something went wrong!\n'
                                'Error: group_equipment')

            if equipment.weight is not None:
                total_weight += equipment.weight

        equipments = {
            'ARMORS': armors,
            'WEAPONS': weapons,
            'ADVENTURING GEARS': gear,
            'TOOLS': tools,
            'MOUNTS AND VEHICLES': mounts,
            'TRINKETS': trinkets,
            'WEIGHT': total_weight,
            'ARMOR EQUIPPED': [],
            'SHIELD EQUIPPED': False
        }

    return equipments


# TODO: remove excessive criteria to reroll when rolling abilities values


def select_equipment(classe, background):
    equipments = None
    end = False
    while not end:
        equipment_choices = classe.equipment_options \
                            + background.equipment_options
        equipment_bought = choose_or_bought()

        if equipment_bought == 'EXIT':
            equipments = 'EXIT'
            end = True
        elif equipment_bought == 'GO BACK':
            equipments = 'GO BACK'
            end = True

        if equipment_bought is True:
            new_equipments, new_wealth = buy_equipment(classe.starting_wealth)

            if new_equipments != 'GO BACK' and new_equipments is not None:
                end = True
                equipments = new_equipments
                classe.wealth = new_wealth
        elif equipment_bought is False:
            classe.wealth = -1
            equipments = choose_equipment(equipment_choices)

            if equipments != 'GO BACK' and equipments != 'EXIT':
                end = True
            elif equipments == 'EXIT':
                end = True
                equipments = 'EXIT'

        if end and equipments != 'EXIT' and equipment_bought != 'GO BACK':
            equipments = create_simple_list(equipments)
            equipments = group_equipment(equipments)

    return equipments


def loop_through_functions(variables, functions_order):
    end = False
    all_defined = True
    last_choice = None
    function_number = 0
    while not end:
        try:
            function_info = functions_order[function_number]
            variable_key = function_info[0]
            function = function_info[1]
            parameters_keys = function_info[2]
            asks_user = function_info[3]

            parameters = []
            for key in parameters_keys:
                parameters.append(variables[key])

            result = function(*parameters)

            if last_choice == 'GO BACK' \
                    and ((asks_user == 'SOMETIMES' and result is None)
                         or asks_user == 'NEVER'):
                if function_number != 0:
                    function_number -= 1
                else:
                    all_defined = False
                    end = True
            else:
                last_choice = result

                if result not in ['GO BACK', 'EXIT']:
                    function_number += 1
                    variables[variable_key] = result
                elif result is None:
                    raise Exception(f'{variable_key} = None.')
                elif result == 'GO BACK':
                    if function_number != 0:
                        function_number -= 1
                    else:
                        all_defined = False
                        variables[variable_key] = 'GO BACK'
                        end = True
                elif result == 'EXIT':
                    all_defined = False
                    variables[variable_key] = 'EXIT'
                    end = True

        except IndexError:
            end = True

    return all_defined


def select_background_speciality(background, ):
    background_speciality = None
    if background.possible_specialities:
        background_speciality = select(
            options=background.possible_specialities,
            prompt=f'As a {background.name}, you can choose something special.',
            single_item=True
        )

    return background_speciality


def select_personality_trait(background):
    personality_trait = select(
        options=background.possible_traits + ['RANDOM', 'WRITE IN'],
        prompt='Choose your psychology trait.',
        single_item=True
    )
    personality_trait = deal_other_options(
        characteristic=personality_trait,
        characteristic_list=background.possible_traits
    )

    return personality_trait


def select_ideal(background, alignment):
    possible_ideals = []
    for ideal in background.possible_ideals:
        if ideal[1] in alignment:
            possible_ideals.append(ideal[0])

    ideal = select(
        options=possible_ideals + ['RANDOM', 'WRITE IN'],
        prompt='Choose your ideal.',
        single_item=True
    )
    ideal = deal_other_options(
        characteristic=ideal,
        characteristic_list=background.possible_ideals
    )

    return ideal


def select_bond(background):
    bond = select(
        options=background.possible_bonds + ['RANDOM', 'WRITE IN'],
        prompt='Choose your bond.',
        single_item=True
    )
    bond = deal_other_options(
        characteristic=bond,
        characteristic_list=background.possible_bonds,
    )

    return bond


def select_flaw(background):
    flaw = select(
        options=background.possible_flaws + ['RANDOM', 'WRITE IN'],
        prompt='Choose your flaw.',
        single_item=True
    )
    flaw = deal_other_options(
        characteristic=flaw,
        characteristic_list=background.possible_flaws
    )

    return flaw


def select_psychological(alignment, background):
    variables = {
        'BACKGROUND': background,
        'ALIGNMENT': alignment,
        'SPECIALITY': None,
        'TRAIT': None,
        'IDEAL': None,
        'BOND': None,
        'FLAW': None,
    }

    functions_order = [
        ['SPECIALITY', select_background_speciality, ['BACKGROUND'],
         'SOMETIMES'],
        ['TRAIT', select_personality_trait, ['BACKGROUND'], 'ALWAYS'],
        ['IDEAL', select_ideal, ['BACKGROUND', 'ALIGNMENT'], 'ALWAYS'],
        ['BOND', select_bond, ['BACKGROUND'], 'ALWAYS'],
        ['FLAW', select_flaw, ['BACKGROUND'], 'ALWAYS']
    ]

    if loop_through_functions(variables, functions_order):
        background.background_speciality = variables['SPECIALITY']
        background.personality_trait = variables['TRAIT']
        background.ideal = variables['IDEAL']
        background.bond = variables['BOND']
        background.flaw = variables['FLAW']
    else:
        if 'GO BACK' in variables.values():
            return 'GO BACK'
        elif 'EXIT' in variables.values():
            return 'EXIT'

    clear_terminal()

    return background


def select_race():
    race = select(
        options=index['RACES'],
        prompt='In the world of Dungeons and Dragons, there are 14 races...',
        show_type='key',
        return_type='key',
        single_item=True
    )
    clear_terminal()

    # Every different color of a Dragonborn came with different features, so
    # it is treated each as a subrace, having is own race object
    if race == 'DRAGONBORN':
        race = select(
            options=index['DRAGONBORN'],
            prompt='A Dragonborn can be of many colors. Choose your own:',
            show_type='key',
            return_type='value',
            single_item=True
        )
        clear_terminal()
    elif race in ['GO BACK', 'EXIT']:
        pass
    else:
        race = index['RACES'][race]

    return race


def select_class():
    # Get Class name
    classe = select(
        options=index['CLASSES'],
        prompt='In Dungeons and Dragons, there are 12 different classes:',
        single_item=True
    )
    clear_terminal()

    return classe


def select_background_feature(background):
    feature = background.feature
    if background.feature_options:
        feature = select(
            options=background.feature_options,
            prompt={f'As a {background.name}, you can choose between the '
                    f'features'},
        )

    return feature


def create_proficiencies(race, classe, background, skills_proficiency):
    # Unite weapons with proficiency
    weapon_proficiency = unite_proficiency(
        race.weapon_proficiency,
        classe.weapon_proficiency
    )

    # Unite armors with proficiency
    armor_proficiency = unite_proficiency(
        race.armor_proficiency,
        classe.armor_proficiency
    )

    # Unite tools with proficiency
    tools_proficiency = unite_proficiency(
        race.tools_proficiency,
        classe.tools_proficiency,
        background.tools_proficiency
    )

    proficiencies = {
        'VALUE': classe.proficiency,
        'SAVING THROWS': classe.saving_throw_proficiency,
        'SKILLS': skills_proficiency,
        'ARMORS': armor_proficiency,
        'WEAPONS': weapon_proficiency,
        'TOOLS': tools_proficiency
    }

    return proficiencies


def create_new_character():
    """
    Deals with all the info that a new character must have and
    then creates this character with the info provided by the user.
    :return: object of the class Character
    """

    variables = {
        'RACE': None,
        'CLASS': None,
        'BACKGROUND': None,
        'LEVEL': None,
        'ABILITIES': None,
        'ALIGNMENT': None,
        'SKILLS PROFICIENCY': None,
        'LANGUAGES': None,
        'EQUIPMENTS': None,
        'PERSONAL INFO': None,
        'PROFICIENCIES': None,
        'FEATURE': None,
        'TOOLS': None
    }

    functions_order = [
        ['RACE', select_race, [], 'ALWAYS'],
        ['CLASS', select_class, [], 'ALWAYS'],
        ['BACKGROUND', select_background, [], 'ALWAYS'],
        ['LEVEL', select_level, [], 'ALWAYS'],
        ['ABILITIES', create_abilities,
         ['CLASS', 'RACE', 'ABILITIES'], 'ALWAYS'],
        ['CLASS', create_class, ['CLASS', 'LEVEL', 'ABILITIES'], 'NEVER'],
        ['ALIGNMENT', get_alignment, [], 'ALWAYS'],
        ['FEATURE', select_background_feature, ['BACKGROUND'], 'SOMETIMES'],
        ['SKILLS PROFICIENCY', select_skills,
         ['RACE', 'CLASS', 'BACKGROUND'], 'ALWAYS'],
        ['LANGUAGES', select_new_languages, ['BACKGROUND', 'RACE'], 'ALWAYS'],
        ['TOOLS', select_proficient_tool,
         ['RACE', 'CLASS', 'BACKGROUND'], 'SOMETIMES'],
        ['EQUIPMENTS', select_equipment, ['CLASS', 'BACKGROUND'], 'ALWAYS'],
        ['BACKGROUND', select_psychological,
         ['ALIGNMENT', 'BACKGROUND'], 'ALWAYS'],
        ['PERSONAL INFO', get_personal_info, ['RACE'], 'ALWAYS'],
        ['PROFICIENCIES', create_proficiencies,
         ['RACE', 'CLASS', 'BACKGROUND', 'SKILLS PROFICIENCY'], 'NEVER']
    ]

    if loop_through_functions(variables, functions_order):

        variables['BACKGROUND'].feature = variables['FEATURE']
        try:
            variables['RACE'].tools_proficiency = variables['TOOLS']['RACE']
            variables['CLASS'].tools_proficiency = variables['TOOLS']['CLASS']
            variables['BACKGROUND'].tools_proficiency = \
                variables['TOOLS']['BACKGROUND']
        except (KeyError, TypeError):
            pass

        character = Character(
            race=variables['RACE'],
            background=variables['BACKGROUND'],
            classe=variables['CLASS'],
            abilities=variables['ABILITIES'],
            alignment=variables['ALIGNMENT'],
            personal_info=variables['PERSONAL INFO'],
            proficiencies=variables['PROFICIENCIES'],
            languages=variables['LANGUAGES'],
            equipments=variables['EQUIPMENTS'],
        )

        # Checks if character is Drow and, if so, adds the proper spells
        race_magic(
            race_name=character.general_info['RACE'],
            level=1,
            magical_ability=character.magical_ability
        )

        character.xp = character.xp_by_level[character.general_info['LEVEL']]
        for _ in range(character.general_info['LEVEL'], character.real_level):
            level_up(character)

        return character
    else:
        return None


def check_files():
    """
    Check if the necessary folder with the saved sheets is in order
    :return: the path of the folder of the sheets
    """
    parent = Path(__file__).absolute().parent
    sheets_folder = parent.joinpath('Files/Sheets')
    index_file = sheets_folder.joinpath('index.txt')

    if not sheets_folder.exists():
        sheets_folder.mkdir(parents=True)

    if not index_file.exists():
        sheets_files = get_children(sheets_folder)
        index_file.touch()

        for sheet in sheets_files:
            with open(sheet, 'rb') as file:
                character = pickle.load(file)

            with open(index_file, 'a') as file:
                file.write(sheet + '\n')
                file.write(character.personal_info["CHARACTER'S NAME"] + '\n')
                file.write(character.general_info['RACE'] + '\n')
                file.write(character.general_info['CLASS'] + '\n')
                file.write(str(character.general_info['LEVEL']) + '\n')
                file.write(character.general_info['BACKGROUND'] + '\n')

    return sheets_folder


def save_sheet(character):
    folder = check_files()
    path = folder.joinpath(character.personal_info["CHARACTER'S NAME"] + '.txt')
    exists = path.exists()

    with open(path, 'wb') as new_file:
        pickle.dump(character, new_file)

    if not exists:
        string_path = path.as_posix()
        index_path = folder.joinpath('index.txt')
        with open(index_path, 'a') as index_file:
            index_file.write(string_path + '\n')
            index_file.write(character.personal_info["CHARACTER'S NAME"] + '\n')
            index_file.write(character.general_info['RACE'] + '\n')
            index_file.write(character.general_info['CLASS'] + '\n')
            index_file.write(str(character.general_info['LEVEL']) + '\n')
            index_file.write(character.general_info['BACKGROUND'] + '\n')


def show_sheets():
    """
    Prints a formatted table with the main info of the character for the user
    to choose.
    :return: dictionary with the number associated with all the sheets
    """
    folder = check_files()
    sheets_index = folder.joinpath('index.txt')
    sheets_path = {}
    number_sheets = len(get_children(folder)) - 1
    headline = (
        '(##)  '
        'Name                      '
        'Race                '
        'Class      '
        'Lv  '
        'Background   \n'
    )

    files_info = {}
    with open(sheets_index, 'r') as file_object:
        for _ in range(number_sheets):
            file = file_object.readline()[:-1]

            name = file_object.readline()[:-1]
            name = name.strip().split(' ')
            if len(name) > 1:  # If the character has more than one name
                name = name[0] + ' ' + name[-1]  # Only first and last names
            else:
                name = name[0]  # The only name he/she has.

            name = f'{name:.24s}'  # Max length of 24 characters
            key = name.upper()  # To use in the dictionary
            name = f'{name:24s}'  # Must occupy 24 characters
            info = ' ' + name + '  '

            race = file_object.readline()[:-1]
            race = f'{race:.18s}'  # Max length of 10 characters
            race = f'{race:18s}'  # Must occupy 10 characters
            info += race + '  '

            classe = file_object.readline()[:-1]
            classe = f'{classe:.9s}'  # Max length of 9 characters
            classe = f'{classe:9s}'  # Must occupy 9 characters
            info += classe + '  '

            level = file_object.readline()[:-1]
            level = f'{level:.2s}'  # Max length of 2 characters
            level = f'{level:2s}'  # Must occupy 2 characters
            info += level + '  '

            background = file_object.readline()[:-1]
            background = f'{background:.13s}'  # Max length of 13 characters
            background = f'{background:13s}'  # Must occupy 13 characters
            info += background

            files_info[info] = key
            sheets_path[key] = file
    files_info[' GO BACK'] = 'GO BACK'
    sheets_path['GO BACK'] = 'GO BACK'

    answer = select(
        options=files_info,
        prompt=headline,
        show_type='key',
        return_type='value',
        single_item=True,
        go_back=False,
        finish=False
    )

    clear_terminal()

    return sheets_path[answer]


def delete_sheet(sheet):
    # TODO: Change the function of spells to show all spells available per level
    #       if the number of spells known is -1
    folder = check_files()
    index_path = folder.joinpath('index.txt')
    string_path = sheet.as_posix()

    with open(index_path, 'r') as index_file:
        lines = index_file.readlines()
    number_sheets = int(len(lines) / 6)

    saved_sheets = {}
    with open(index_path, 'r') as index_file:
        for _ in range(number_sheets):
            path_read = index_file.readline()
            saved_sheets[path_read[:-1]] = {
                'PATH': path_read,
                'NAME': index_file.readline(),
                'RACE': index_file.readline(),
                'CLASS': index_file.readline(),
                'LEVEL': index_file.readline(),
                'BACKGROUND': index_file.readline()
            }

    saved_sheets.pop(string_path)

    with open(index_path, 'w') as index_file:
        for sheet_to_save in saved_sheets.values():
            index_file.write(sheet_to_save['PATH'])
            index_file.write(sheet_to_save['NAME'])
            index_file.write(sheet_to_save['RACE'])
            index_file.write(sheet_to_save['CLASS'])
            index_file.write(sheet_to_save['LEVEL'])
            index_file.write(sheet_to_save['BACKGROUND'])

    sheet.unlink()


def edit_character(character):
    possible_to_edit = [
        'SPELLS',
        'PERSONAL INFO',
        'ALIGNMENT',
    ]
    if character.sessions == 0:
        possible_to_edit += [
            'SKILLS',
            'RELOCATE ABILITIES',
            'EQUIPMENT',
        ]

    to_edit = None
    while to_edit != 'GO BACK':
        to_edit = select(
            options=possible_to_edit,
            prompt='Select what you want to edit',
            single_item=True,
            finish=False,
        )

        clear_terminal()

        if to_edit == 'EQUIPMENT':
            end = False

            while not end:
                equipment_bought = choose_or_bought()

                if equipment_bought not in ['EXIT', 'GO BACK']:
                    if equipment_bought:
                        new_equipments, new_wealth = buy_equipment(
                            character.backup['CLASS'].starting_wealth
                        )

                        if new_equipments != 'GO BACK':
                            end = True

                            if new_equipments is not None:
                                character.equipments = new_equipments
                                character.wealth = new_wealth
                    else:
                        new_equipments = choose_equipment(
                            character.backup['CLASS'].equipment_options
                        )

                        if new_equipments not in ['GO BACK', 'EXIT']:
                            end = True
                            character.wealth = character.backup['BACKGROUND'] \
                                .wealth
                            character.equipments = new_equipments

                        elif new_equipments == 'EXIT':
                            end = True

                    character.equipments = group_equipment(character.equipments)

                elif equipment_bought == 'EXIT':
                    to_edit = 'GO BACK'

                elif equipment_bought == 'GO BACK':
                    end = True

        elif to_edit == 'RELOCATE ABILITIES':
            values = get_existing_abilities_values(
                character.abilities, character.backup['RACE'].ability_increase)

            character.abilities.values = get_abilities_values(
                values,
                character.general_info['CLASS']
            )

            for ability, increase in \
                    character.backup['RACE'].ability_increase.items():
                character.abilities.increment_ability(ability, increase)

        elif to_edit == 'SKILLS':
            new_skills = select_skills(
                race=character.backup['RACE'],
                classe=character.backup['CLASSE'],
                background=character.backup['BACKGROUND']
            )

            if new_skills != 'GO BACK':
                if new_skills != 'EXIT':
                    character.proficiencies['SKILLS'] = new_skills
                else:
                    to_edit = 'GO BACK'

        elif to_edit == 'SPELLS':
            if character.magical_ability.has_magic:
                end = False
                while not end:
                    cont = True

                    copy_character = copy.deepcopy(character)
                    copy_character.magical_ability.set_cantrips([])
                    new_cantrips = select_cantrips(copy_character)

                    if new_cantrips not in ['EXIT', 'GO BACK']:
                        character.magical_ability.set_cantrips([])
                        character.magical_ability.set_cantrips(new_cantrips)
                    else:
                        cont = False
                        end = True

                        if new_cantrips == ['EXIT']:
                            to_edit = 'GO BACK'

                    if cont:
                        copy_character.magical_ability.set_spells({})
                        new_spells = select_spells(copy_character)

                        if new_spells not in ['EXIT', 'GO BACK']:
                            end = True
                            character.magical_ability.set_spells({})
                            character.magical_ability.set_spells(new_spells)
                        elif new_cantrips == ['EXIT']:
                            end = True
                            to_edit = 'GO BACK'
            else:
                clear_terminal()

                print('You are no coward! No need for magic!')
                print('Press ENTER to continue.')
                input()

        elif to_edit == 'ALIGNMENT':
            option = select(
                options=index['ALIGNMENTS'],
                prompt='In Dungeons and Dragons, '
                       'there are 9 possible alignments.',
                single_item=True,
            )

            if option != 'GO BACK':
                if option != 'EXIT':
                    character.general_info['ALIGNMENT'] = option
                else:
                    to_edit = 'GO BACK'

        elif to_edit == 'PERSONAL INFO':
            options = [
                'PLAYER NAME', 'CHARACTER NAME', 'AGE', 'HEIGHT', 'WEIGHT',
                'EYES COLOR', 'SKIN COLOR', 'HAIR COLOR', 'HISTORY'
            ]

            end = False
            while not end:
                answer = select(
                    options=options,
                    prompt='Select what to edit in your personal info.',
                    single_item=True,
                )

                if answer == 'PLAYER NAME':
                    character.general_info["PLAYER'S NAME"] = get_player_name()
                elif answer == 'CHARACTER NAME':
                    character.general_info["CHARACTER'S NAME"] = get_name()
                elif answer == 'AGE':
                    character.personal_info['AGE'] = get_age(
                        character.backup['RACE'])
                elif answer == 'HEIGHT':
                    character.personal_info['HEIGHT'] = get_height(
                        character.backup['RACE'])
                elif answer == 'WEIGHT':
                    character.personal_info['WEIGHT'] = get_weight()
                elif answer == 'EYES COLOR':
                    character.personal_info['EYE'] = get_eye_color()
                elif answer == 'SKIN COLOR':
                    character.personal_info['SKIN'] = get_skin_color()
                elif answer == 'HAIR COLOR':
                    character.personal_info['HAIR'] = get_hair_color()
                elif answer == 'HISTORY':
                    character.personal_info['HISTORY'] = get_history()
                else:
                    end = True

                    if answer == 'EXIT':
                        to_edit = 'GO BACK'

        clear_terminal()

    return True


"""
def weapon_attack(character):
    clear_terminal()

    str_modifier = character.abilities.score('STR')
    dex_modifier = character.abilities.score('DEX')

    options = {}
    for weapon in character.equipments['WEAPONS']:
        options[f'{weapon.name.title()}'] = weapon
    options['CANCEL'] = 'CANCEL'

    weapon = select(
        options=options,
        prompt='Select a weapon:',
        show_type='key',
        return_type='value',
        single_item=True
    )

    if weapon != 'CANCEL':
        clear_terminal()

        # TODO: Add the selection of different conditions for the attack,
        # 		i.e., stealth, with advantage

        proficiency = False
        ability_modifier = None
        damage = None

        if weapon.name in character.proficiencies['WEAPONS']:
            proficiency = True

        if proficiency:
            proficiency = character.proficiencies['VALUE']
        else:
            proficiency = 0

        if 'FINESSE' in weapon.properties:
            if dex_modifier > str_modifier:
                ability_modifier = dex_modifier
            else:
                ability_modifier = str_modifier

        elif 'THROWN' in weapon.properties:
            answer = select(
                options=['THROW', 'DON\'T THROW'],
                prompt='This weapon may be thrown. What do you desire to do?',
                single_item=True,
                go_back=False
            )

            if answer == 'THROW':
                ability_modifier = dex_modifier
            elif answer == 'DON\'T THROW':
                ability_modifier = str_modifier
            elif answer == 'EXIT':
                return answer

        else:
            for classifications in index['EQUIPMENT']['WEAPON'].values():
                for classification, items in classifications.items():
                    if weapon in items.values():
                        if classification == 'MELEE':
                            ability_modifier = str_modifier
                        elif classification == 'RANGED':
                            ability_modifier = dex_modifier

        if ability_modifier is None:
            raise Exception('Error in weapon_attack!'
                            ' Value of ability_modifier is None!')

        answer = select(
            options=['NONE', 'STEALTH', 'ADVANTAGE', 'DISADVANTAGE'],
            prompt='Are you in a situation that will affect your attack?',
            single_item=True,
            go_back=False,
        )

        loop = 1
        weapon.damage.modifier = ability_modifier
        damage_dice = convert_dice_to_d_format(weapon.damage)
        attack_modifier = ability_modifier + proficiency
        d20 = Dice()
        d20_string = convert_dice_to_d_format(d20)

        if answer != 'EXIT':
            if answer == 'STEALTH':

            elif answer in ['ADVANTAGE', 'DISADVANTAGE']:
                loop = 2

                answer = None
                if answer == 'ADVANTAGE':
                    choose_number = '>'
                elif answer == 'DISADVANTAGE':
                    choose_number = '<'
        else:
            return answer

        results = []
        damages = []
        for _ in range(loop):
            result = d20.roll(attack_modifier)

            if result == 20:
                weapon.damage.number = 2
                damage = weapon.damage.roll()
                weapon.damage.number = 1
            else:
                damage = weapon.damage.roll()

        if 

        print(f'You selected {weapon.name.title()}')
        print(f'Your attack is {d20_string}; The damage is {damage_dice}')
        print('Press ENTER to roll your attack...')
        input()

        print(f'Your result is {result}...')
        if result == 20:
            print('Which is a CRITICAL!')
        print(
            f"If you succeed in your attack, you've done a damage of {damage}"
        )

        print('Press ENTER to continue')
        input()
    elif weapon == 'GO BACK' or weapon == 'EXIT':
        return weapon


def skill_check(character):
    # TODO: Finish this function
"""


def use_magic(character):
    clear_terminal()

    if character.magical_ability.has_magic is not None:
        print('This is a beta version of the magic '
              'use in Character Sheet Manager.')
        loop = True
        while loop:
            max_slot = None
            for slot, spells in character.magical_ability.spell_slots.items():
                if spells - character.magical_ability.slots_spent[slot] > 0:
                    max_slot = slot

            options = []
            for slot_level in range(max_slot):
                options.append(slot_level + 1)

            answer = select(
                options=options,
                prompt='Select the spell slot desired '
                       'to spent to cast this spell!',
                single_item=True,
            )

            if answer == 'GO BACK':
                return answer
            elif answer == 'EXIT':
                return answer
            else:
                character.magical_ability.slots_spent[answer] += 1
    else:
        print('Your character has no access to magic.')
        input()

        clear_terminal()

    return None


def equip_armor(character):
    loop = True
    while loop:
        armors = {}
        for armor in character.equipments['ARMORS']:
            if armor == character.equipments['ARMOR EQUIPPED']:
                pass
            elif character.equipments[
                'SHIELD EQUIPPED'] and armor.name == 'SHIELD':
                pass
            else:
                armors[armor.name] = armor

        if character.equipments['ARMOR EQUIPPED']:
            armors['REMOVE ARMOR'] = 'REMOVE ARMOR'

            armor_equipped = character.equipments['ARMOR EQUIPPED']
            text = f'You are wearing a {armor_equipped.name.title()} ' \
                   f'armor - {armor_equipped.armor_type.title()}.\n'
            text += f'Its Armor Class is of {armor_equipped.armor_class}.\n'

            if armor_equipped.strength:
                text += f'To wear it, you must have a Strength of value ' \
                        f'{armor_equipped.strength}.\n'

            if armor_equipped.dex_max:
                text += 'Your maximum dexterity modifier given by this armor ' \
                        f'is of {armor_equipped.dex_max}.\n'

            if armor_equipped.stealth_disadvantage:
                text += 'It also gives you disadvantage in stealth checks!\n'
        else:
            text = 'You are currently not wearing any armor.\n'

        if character.equipments['SHIELD EQUIPPED']:
            armors['REMOVE SHIELD'] = 'REMOVE SHIELD'

            text += '\nYou are also wearing a shield!\n'
            text += 'The shield adds 2 to your general Armor Class.\n'

        text += '\nSelect an armor to equip in your character.\n'
        text += 'Be aware that, doing that, you will be replacing your current' \
                ' armor, if there is one\n'

        answer = select(
            options=armors,
            prompt=text,
            show_type='key',
            return_type='value',
            single_item=True
        )

        if answer not in ['GO BACK', 'EXIT']:
            if answer == 'REMOVE ARMOR':
                character.equipments['ARMOR EQUIPPED'] = []

            elif answer == 'REMOVE SHIELD':
                character.equipments['SHIELD EQUIPPED'] = False

            elif answer.name == 'SHIELD':
                character.equipments['SHIELD EQUIPPED'] = True

            else:
                character.equipments['ARMOR EQUIPPED'] = answer

            clear_terminal()
            character.general_stats['AC'] = 10 \
                                            + character.abilities.score('DEX')
            print(f'Dex mod: {character.abilities.score("DEX")}')
            print(f'AC: {character.general_stats["AC"]}')

            if character.equipments['SHIELD EQUIPPED'] is True:
                print(f'Shield: {shield.armor_class}')
                character.general_stats['AC'] += shield.armor_class
                print(f'AC: {character.general_stats["AC"]}')

            if character.equipments['ARMOR EQUIPPED']:
                equipped_armor = character.equipments['ARMOR EQUIPPED']
                print(f'Armor: {equipped_armor.armor_class}')
                character.general_stats['AC'] += equipped_armor.armor_class
                print(f'AC: {character.general_stats["AC"]}')

            input()
            clear_terminal()

            save_sheet(character)

        elif answer == 'GO BACK':
            loop = False
        elif answer == 'EXIT':
            return 'EXIT'

    return None


def rest(character):
    answer = select(
        options=['LONG REST', 'SHORT REST'],
        prompt='What kind of rest would you like to take?',
        single_item=True
    )

    if answer == 'LONG REST':
        for level in character.magical_ability.slots_spent.keys():
            character.magical_ability.slots_spent[level] = 0

        character.general_stats['CURRENT HP'] = \
            character.general_stats['MAXIMUM HP'] \
            + character.general_stats['TEMPORARY HP']

    elif answer == 'SHORT REST':
        if character.general_stats['CURRENT HP'] \
                < character.general_stats['MAXIMUM HP'] \
                + character.general_stats['TEMPORARY HP']:
            if character.general_stats['USED HIT DICE'] \
                    < character.general_info['LEVEL']:
                # MULTICLASS
                number = character.general_stats['HIT DICE'].max
                options = {}
                for level in range(character.general_info['LEVEL']):
                    dice = Dice(level + 1, number)
                    options[convert_dice_to_d_format(dice)] = dice

                answer = select(
                    options=options,
                    prompt='You can use an certain amount of hit dice to '
                           'recover your Health Points.',
                    show_type='key',
                    return_type='value',
                    single_item=True
                )

                if answer == 'GO BACK' or answer == 'EXIT':
                    return answer
                else:
                    recovered_hp = answer.roll(character.abilities.score('CON'))

                    if character.general_info['CURRENT HP'] \
                            + recovered_hp \
                            > character.general_info['MAXIMUM HP'] \
                            + character.general_info['TEMPORARY HP']:
                        character.general_info['CURRENT HP'] = \
                            character.general_info['MAXIMUM HP'] \
                            + character.general_info['TEMPORARY HP']
                    else:
                        character.general_info['CURRENT HP'] += recovered_hp

                    character.general_stats['USED HIT DICE'] = answer.number

    elif answer == 'EXIT':
        return answer

    return None


def death_check(character):
    d20 = Dice()

    end = False
    while not end:
        clear_terminal()

        print('Oh, no! It appears your character has a negative HP!')
        print('According to the rules, you must succeed in three death '
              'saving throws.\n')

        print('You already have:')
        print(f'- {character.checks_succeeded} successful checks.')
        print(f'- {character.checks_failed} failed checks.\n')

        print('Press ENTER to do another check.')
        input()

        clear_terminal()
        result = d20.roll()

        print(f'You have rolled a {result}.')

        if result == 1:
            print('It is a critical failure! It counts twice.')
            character.checks_failed += 2
        elif result < 10:
            print('It is a failure!')
            character.checks_failed += 1
        elif result < 20:
            print('It is a success!')
            character.checks_succeeded += 1
        else:  # result == 20
            print('It is a critical success!')
            character.checks_succeeded += 2

        if character.checks_succeeded >= 3 \
                or character.checks_failed >= 3:
            end = True

            if character.checks_succeeded >= 3:
                character.general_stats['CURRENT HP'] = 0
                character.checks_failed = 0
                character.checks_succeeded = 0
                print('')
                print('You have now 3 successes. You have now 0 HP')
            else:  # character.checks_failures >= 3
                character.dead = True
                print('')
                print('You have now 3 failures.')
                print('Unfortunately, you died.')


def modify_hp(character):
    loop = True
    while loop:
        answer = select(
            options=[
                'TAKE DAMAGE', 'RECOVER HP',
                'REMOVE TEMPORARY HP', 'ADD TEMPORARY HP',
            ],
            prompt='Current HP/Temporary HP/Maximum HP: '
                   f'{character.general_stats["CURRENT HP"]}/'
                   f'{character.general_stats["TEMPORARY HP"]}/'
                   f'{character.general_stats["MAXIMUM HP"]}\n\n'
                   'You have a few options to modify '
                   'your HP. Choose the adequate.',
            single_item=True
        )

        if answer == 'EXIT':
            return answer

        elif answer == 'GO BACK':
            loop = False

        elif answer == 'TAKE DAMAGE':
            damage = get_a_number('Type the number of damage taken.')

            if damage is not None:
                character.general_stats['CURRENT HP'] -= damage

        elif answer == 'RECOVER HP':
            recovered = get_a_number(
                'Type the number of HP recovered.\n'
                "If want to go back, just type anything that's not a number."
            )

            if recovered is not None:
                if character.general_stats['CURRENT HP'] + recovered \
                        <= character.general_stats['MAXIMUM HP'] \
                        + character.general_stats['TEMPORARY HP']:
                    character.general_stats['CURRENT HP'] += recovered
                else:
                    character.general_stats['CURRENT HP'] = \
                        character.general_stats['MAXIMUM HP'] \
                        + character.general_stats['TEMPORARY HP']

        elif answer == 'ADD TEMPORARY HP':
            temporary = get_a_number(
                f'Your current temporary HP is '
                f'{character.general_stats["TEMPORARY HP"]}\n\n'
                'Type the number of added temporary HP.'
            )

            if temporary is not None:
                character.general_stats['TEMPORARY HP'] += temporary

        elif answer == 'REMOVE TEMPORARY HP':
            temporary = get_a_number(
                'Your current temporary HP is of '
                f'{character.general_stats["TEMPORARY HP"]}\n\n'
                'Type the number of removed temporary HP.'
            )

            if temporary is not None:
                character.general_stats['TEMPORARY HP'] -= temporary

        if character.general_stats['CURRENT HP'] \
                + character.general_stats['TEMPORARY HP'] \
                <= -character.general_stats['MAXIMUM HP']:
            print('You died!')
            print('The exceeding damage is bigger than your maximum HP.')
            print('Press ENTER to continue...')
            input()

        elif character.general_stats['CURRENT HP'] \
                + character.general_stats['TEMPORARY HP'] \
                <= 0:
            character.checks_failed = 0
            character.checks_succeeded = 0

            death_check(character)

        elif character.general_stats['CURRENT HP'] \
                + character.general_stats['TEMPORARY HP'] \
                == 0:
            clear_terminal()
            print('Your HP reached 0. You fall unconscious!')
            print('Press ENTER to continue...')
            input()
            clear_terminal()

    return None


def modify_equipment(character):
    new_equipment, new_wealth = buy_equipment(
        starting_wealth=character.wealth,
        fixed_price=False
    )

    if new_equipment is None:
        return 'EXIT'

    new_equipment = group_equipment(new_equipment)

    clear_terminal()
    print(character.equipments)
    print(new_equipment)
    input()
    clear_terminal()

    for category, equipments in new_equipment.items():
        print(category)
        print(equipments)
        print(character.equipments[category])
        input()
        clear_terminal()
        character.equipments[category] += equipments

    character.wealth = new_wealth

    return None


def add_xp(character):
    new_xp = get_a_number('Type the number of new XP')

    if new_xp is not None:
        character.general_info['XP'] += new_xp

        level_up(character)


def play(character):
    answer = None
    what_to_do = [
        'EQUIP ARMOR',
        'MODIFY EQUIPMENT',
        'MODIFY HP',
        'SPELL SLOTS',
        'ADD XP',
        'TAKE A REST',
        'DIE',
    ]

    while answer != 'GO BACK':
        answer = select(
            options=what_to_do,
            prompt='You are in the play mode. What you want to do?',
            single_item=True,
            finish=False
        )

        if answer == 'EQUIP ARMOR':
            result = equip_armor(character)

            if result == 'EXIT':
                answer = 'GO BACK'

        elif answer == 'TAKE A REST':
            result = rest(character)

            if result == 'EXIT':
                answer = 'GO BACK'

        elif answer == 'MODIFY HP':
            result = modify_hp(character)

            if result == 'EXIT':
                answer = 'GO BACK'

        elif answer == 'MODIFY EQUIPMENT':
            result = modify_equipment(character)

            if result == 'EXIT':
                answer = 'GO BACK'

        elif answer == 'SPELL SLOTS':
            result = use_magic(character)

            if result == 'EXIT':
                answer = 'GO BACK'

        elif answer == 'ADD XP':
            add_xp(character)


def open_sheet(sheet):
    options = [
        'SEE SHEET', 'EDIT SHEET', 'PLAY WITH SHEET', 'DELETE SHEET'
    ]
    end = False

    with open(sheet, 'rb') as file_object:
        character = pickle.load(file_object)

    while not end:
        choice = select(
            options=options,
            prompt='What you want to do?',
            single_item=True,
            go_back=False,
        )
        sheet = Path(sheet)

        if choice == 'SEE SHEET':
            show_character(character)
        elif choice == 'EDIT SHEET':
            succeeded = edit_character(character)

            if succeeded is True:
                save_sheet(character)
        elif choice == 'PLAY WITH SHEET':
            play(character)
            save_sheet(character)
        elif choice == 'DELETE SHEET':
            delete_sheet(sheet)
            end = True
        else:
            end = True

        clear_terminal()


def create_new_sheet(character):
    """
    Stores the character object in a file and adds its info to the index
    :param character: object of the class character
    :return: boolean if the sheet was created successfully or not
    """
    loop = True
    cancel = False
    folder = check_files()
    new_path = folder.joinpath(
        character.personal_info["CHARACTER'S NAME"] + '.txt'
    )

    while loop:
        if new_path.exists():
            options_text = [
                'RENAME CHARACTER',
                'OVERWRITE SHEET',
                'CANCEL NEW CHARACTER'
            ]
            answer = select(
                options=options_text,
                prompt='It looks like a sheet with this name already exists.',
                single_item=True
            )

            if answer == 'RENAME CHARACTER':
                character.personal_info["CHARACTER'S NAME"] = get_name()
                new_path = folder.joinpath(
                    character.personal_info["CHARACTER'S NAME"] + '.txt'
                )
            elif answer == 'OVERWRITE SHEET':
                loop = False
            elif answer == 'CANCEL NEW CHARACTER':
                cancel = True
                loop = False

            clear_terminal()
        else:
            loop = False

    if not cancel:
        save_sheet(character)
        return True
    else:
        return False


def routine_preparation():
    check_files()
    columns, lines = os.get_terminal_size()

    while columns != 80:
        print(
            'Please set your window for the width of 80 and then press '
            'ENTER to continue'
        )
        input()

        columns, lines = os.get_terminal_size()

    clear_terminal()


def level_up(character):
    if character.general_info['XP'] >= character.xp_by_level[
        character.general_info['LEVEL'] + 1]:
        character.general_info['LEVEL'] += 1

        if character.general_info['LEVEL'] in [4, 8, 12, 16, 19]:
            answer = None

            added_points = {
                'STR': 0,
                'DEX': 0,
                'CON': 0,
                'INT': 0,
                'WIS': 0,
                'CHA': 0
            }

            points_to_increase = 2
            while answer != 'CONFIRM':
                prompt = f'You have {points_to_increase} points ' \
                         f'to add in abilities'

                options = {}
                if points_to_increase > 0:
                    for ability, score in character.abilities.values.items():
                        if score < 20:
                            long_ability = index['ABILITIES'][ability]
                            key = f'{long_ability.title()}: ' \
                                  f'{score + added_points[ability]}'
                            options[key] = ability

                if points_to_increase == 0:
                    options['Confirm new values'] = 'CONFIRM'
                options['Restart values to original'] = 'RESTART'

                answer = select(
                    options=options,
                    prompt=prompt,
                    show_type='key',
                    return_type='value',
                    single_item=True,
                )

                if answer != 'RESTART' and answer != 'CONFIRM':
                    added_points[answer] += 1
                    points_to_increase -= 1
                elif answer == 'RESTART':
                    points_to_increase = 2
                    added_points = {
                        'STR': 0,
                        'DEX': 0,
                        'CON': 0,
                        'INT': 0,
                        'WIS': 0,
                        'CHA': 0
                    }

            for ability, increase in added_points.items():
                character.abilities.increment_ability(ability, increase)

        con_modifier = character.abilities.score('CON')
        hp_addition = character.general_stats['HIT DICE'].roll(con_modifier)
        character.general_stats['MAXIMUM HP'] += hp_addition
        character.general_stats['CURRENT HP'] += hp_addition
        character.general_stats['HIT DICE'].number += 1
        # MULTICLASS

        character.specialization['NAME'] = character.specialization_check(
            character.general_info['LEVEL'],
            character.specialization['LEVEL'],
            character.specialization['ALL FEATURES'],
            character.specialization['NAME'],
        )
        character.specialization['FEATURES'] = \
            character.select_specialization_features(
                level=character.general_info['LEVEL'],
                specialization_level=character.specialization['LEVEL'],
                specializations_features=character.specialization[
                    'ALL FEATURES'],
                specialization=character.specialization['NAME']
            )

        specializations_w_magic = ['ELDRITCH KNIGHT', 'ARCANE TRICKSTER']
        if character.specialization['NAME'] in specializations_w_magic:
            character.magical_ability.has_magic = True

        if character.general_info['CLASS'] in ['PALADIN', 'RANGER']:
            if character.general_info['LEVEL'] >= 2:
                character.magical_ability.has_magic = True

        # TODO: prepare the code to accept classes that must prepare spells
        # if character.magical_ability.prepared_spell is True:

        character.proficiencies['VALUE'] = character.backup[
            'CLASS'].proficiency_by_level[character.general_info['LEVEL']]

        character.features['CLASS'] += character.backup['CLASS'].all_features[
            character.general_info['LEVEL']
        ]
        try:
            character.features['SPECIALIZATION'] += character.specialization[
                'ALL FEATURES'][character.general_info['LEVEL']]
        except KeyError:
            pass

        if character.magical_ability.has_magic is not None:
            character.magical_ability.cantrips_known += \
                character.magical_ability.cantrips_by_level[
                    character.general_info['LEVEL']
                ]

            character.magical_ability.spells_known += character.magical_ability \
                .spells_by_level[character.general_info['LEVEL']]

            character.magical_ability.spell_slots = character.magical_ability. \
                spell_slots_by_level[character.general_info['LEVEL']]

        race_magic(
            race_name=character.general_info['RACE'],
            level=character.general_info['LEVEL'],
            magical_ability=character.magical_ability
        )


def menu():
    """
    Creates a menu for the user to choose what he wants to do
    :return:
    """
    routine_preparation()
    end = False

    while not end:
        choices = ['NEW SHEET', 'OPEN SHEET']
        choice = select(
            options=choices,
            prompt='Welcome to Character Sheets Manager!\n',
            single_item=True,
            go_back=False
        )
        clear_terminal()

        if choice == 'NEW SHEET':
            character = create_new_character()

            if character is not None:
                create_new_sheet(character)

        elif choice == 'OPEN SHEET':
            sheet_path = show_sheets()

            while sheet_path != 'GO BACK':
                open_sheet(sheet_path)
                sheet_path = show_sheets()

        elif choice == 'EXIT':
            end = True