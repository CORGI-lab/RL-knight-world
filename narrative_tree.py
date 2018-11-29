tree = {'leave swamp': {
    'go to kingdom': {
        'get slip from king': {
            'go to armory': {
                'give blacksmith slip': {
                    'get sword from blacksmith': {
                        'go to tower': {
                            'get amulet from wizard': {
                                'go to cave': {
                                    'kill dragon': {},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
    'go to armory': {
        'kill blacksmith': {  # with your hands
            'steal sword': {
                'go to tower': {
                    'get amulet from wizard': {
                        'go to cave': {
                            'kill dragon': {},
                        },
                    },
                },
            },
        },
    },
    'go to tower': {
        'get amulet from wizard': {
            'go to kingdom': {
                'get slip from king': {
                    'go to armory': {
                        'give blacksmith slip': {
                            'get sword from blacksmith': {
                                'go to cave': {
                                    'kill dragon': {},
                                },
                            },
                        },
                    },
                },
            },
            'go to armory': {
                'kill blacksmith': {
                    'steal sword': {
                        'go to cave': {
                            'kill dragon': {},
                        },
                    },
                },
            },
        },
    },
}}
