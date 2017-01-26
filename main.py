import game

app = game.Game()
app.new()
app.show_start_screen()

while app.running:
    app.run()
