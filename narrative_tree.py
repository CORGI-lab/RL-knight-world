tree = {'leave swamp': {
  'go to kingdom': {
    'ask king for slip': {
      'go to forge': {
        'give blacksmith slip from king': {
          'ask blacksmith for sword': {
            'go to tower': {
              'ask wizard for amulet': {
                'go to cave': {
                  'kill dragon': {}}}}}}}}},
  'go to forge': {
    'kill blacksmith': {  # with your hands
      'steal sword': {
        'go to tower': {
          'steal amulet': {
            'go to cave': {
              'kill dragon': {}}}}}}},
  'go to tower': {
    'ask wizard for amulet': {
      'go to kingdom': {
        'ask king for slip': {
          'go to forge': {
            'give blacksmith slip from king': {
              'get sword from blacksmith': {
                'go to cave': {
                  'kill dragon': {}}}}}}},
      'go to forge': {
        'kill blacksmith': {
          'steal sword': {
            'go to cave': {
              'kill dragon': {}}}}}}}}}

scores = {
 'steal sword': 0.4273727,
 'kill blacksmith': 0.4383431,
 'steal amulet': 0.4772043,
 'go to cave': 0.45955008,
 'go to forge': 0.49036837,
 'ask blacksmith for sword': 0.49806365,
 'go to tower': 0.45170587,
 'ask wizard for amulet': 0.5262374,
 'go to kingdom': 0.5286611,
 'leave swamp': 0.41815662,
 'get sword from blacksmith': 0.48302805,
 'kill dragon': 0.3663328,
 'ask king for slip': 0.5143399,
 'give blacksmith slip from king': 0.5256291,
 }
