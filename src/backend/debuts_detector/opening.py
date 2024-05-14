import pgnhelper.app

a = pgnhelper.app.PgnHelper(
    'addeco',
    inpgnfn='Round_1.pgn',
    outpgnfn='Round1_with_opening.pgn',
    inecopgnfn='eco.pgn')
a.start()
