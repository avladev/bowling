# Bowling
This is a simple bowling score calculator application writen in Django.
It allows a single player to create a game and get scoring after each roll.

# URLs
## Create game
```
POST /game/
Params: None
Returns: Game information
```

## Get game score
```
GET /game/
Params: {game: int}
Returns: Game information
```

## Do roll
```
POST /roll/
Params: {game: int, roll: int}
Returns: Game information
```
