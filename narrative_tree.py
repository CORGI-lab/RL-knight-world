tree = {'leave swamp': {
    'go to kingdom': {
        'ask king for slip': {
            'go to forge': {
                'give blacksmith slip from king': {
                    'ask blacksmith for sword': {
                        'go to tower': {
                            'ask wizard for amulet': {
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
    'go to forge': {
        'kill blacksmith': {  # with your hands
            'steal sword': {
                'go to tower': {
                    'steal amulet': {
                        'go to cave': {
                            'kill dragon': {},
                        },
                    },
                },
            },
        },
    },
    'go to tower': {
        'ask wizard for amulet': {
            'go to kingdom': {
                'ask king for slip': {
                    'go to forge': {
                        'give blacksmith slip from king': {
                            'get sword from blacksmith': {
                                'go to cave': {
                                    'kill dragon': {},
                                },
                            },
                        },
                    },
                },
            },
            'go to forge': {
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
