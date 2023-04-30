# Brick Breaker
A classic brick-breaking game built with Pygame. Control the paddle to bounce the ball and destroy bricks, clear all the bricks to progress to the next level. The game features different difficulty settings, customizable controls, power-ups, and game over screen.


## Table of Contents
* Installation
* Usage
* Game Objects
* Game Menus and Screens
* Credits

## Installation
1. Install Python (3.6 or higher)
2. Install Pygame:
```
pip install pygame
```
3. Clone the repository or download the zip file:
```
git clone https://github.com/CommanderOutpost/Brick-Breaker.git
```
4. Place required assets (images, fonts, and sounds) in the specified file paths.

## Usage
To play the game, simply run the brick_breaker.py script in a Python environment:
```
python brick_breaker.py
```

## Game Objects
The game consists of the following objects:

* Brick: The bricks the player must destroy.
* Paddle: The paddle the player controls to bounce the ball.
* Ball: The ball that destroys bricks upon collision.
* PowerUp: Power-ups that can affect the paddle's size and the ball's speed.
* Explosion: Visual effect for brick destruction.

## Game Menus and Screens
The game features the following menus and screens:

* main_menu(): The main menu where the player can start the game or change settings.
* set_difficulty(): A menu where the player can set the difficulty (Easy, Medium, or Hard) which affects the ball and paddle speed.
* settings(): A menu where the player can choose between keyboard and mouse controls for the paddle.
* game_over(): A game over screen that allows the player to restart the game or quit.

## Credits
Brick Breaker is developed by [CommanderOutpost](https://github.com/CommanderOutpost).
