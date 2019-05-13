#Import modules
from random import randint #Include the randint function from the random module
import pygame #Include the pygame module

#GLOBAL CONSTANTS

#Define colours
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
GREEN    = (  0, 230,  77)
RED      = (255,   0,   0)
BROWN    = (131,  81,  54)
SKYBLUE  = (102, 194, 255)
ORANGE   = (255, 128,   0)
YELLOW   = (255, 255,   0)
PEAGREEN = (  0, 153,   0)
LAVARED  = (255,  50,   0)

#Helper text list
LOGLST   = ["Welcome to The Quest for the Golden Coins", "Press 1 for help text"]


#-------------------------------------------------------------------------------
#Abstract class for a moving sprite
class MovingSprite(pygame.sprite.Sprite):
    
    #ATTRIBUTES
    currentLevel = None
    velocityX    = None
    velocityY    = None
    ammo         = None
    currentFrame = None
    
    #Constructor Method
    def __init__(self):
        
        #Call the parent constructor from sprite library
        super(MovingSprite, self).__init__()
        
        #Sets the surface of sprite
        self.image = pygame.Surface([30, 60])
        self.image.set_colorkey(WHITE)
        
        #Sets default ammo of sprite
        self.ammo = 0
        
        #Set speed to 0 for both horizontal and vertical movement
        self.velocityX = 0
        self.velocityY = 0
        
        #Track the current frame for animation purposes
        self.currentFrame = 0
        
        #Create a rect to set the location of the sprite
        self.rect = self.image.get_rect()
    
    #Updates the sprite's position (runs every frame)
    def update(self):
        
        #Add a value to the player's downward position every frame to simulate gravity
        self.velocityY += 0.45
        
        #Move left and right
        self.rect.x += self.velocityX
            
        #Count the platforms that the sprite collided with when moving left/right
        collisionList = pygame.sprite.spritecollide(self, self.currentLevel.platforms, False)
        
        #Iterate through the platforms
        for item in collisionList:
            #If we are moving right, set sprite's right to the wall/platform's left side
            if (self.velocityX > 0):
                self.rect.right = item.rect.left
            #If we are moving left, do the exact opposite
            else:
                self.rect.left = item.rect.right
        
        #Move up and down
        self.rect.y += self.velocityY
        
        #Count the platforms that the player collided with when moving up/down
        collisionList = pygame.sprite.spritecollide(self, self.currentLevel.platforms, False)
        
        #Iterate through the platforms
        for item in collisionList:
            #If we are moving down, set sprite's bottom to the wall/platform's top side
            if (self.velocityY > 0):
                self.rect.bottom = item.rect.top
            #If we are moving up, do the exact opposite
            else:
                self.rect.top = item.rect.bottom
            self.velocityY = 0
        
        #Add 1 to the current frame
        self.currentFrame += 1
    
    #Makes the sprite jump
    def jump(self):
        
        #Increase y position by 2 to check if it is okay to jump
        self.rect.y += 2
        
        #Make a collision list to check if sprite collides with platform when moved down
        collisionList = pygame.sprite.spritecollide(self, self.currentLevel.platforms, False)
        
        #Reset y position of sprite to original value
        self.rect.y -= 2
        
        #If sprite hit a platform when y pos was increased (means it is on a platform), 
        #or if the sprite is on the ground, make sprite jump
        if (len(collisionList) > 0 or self.rect.y > 717):
            self.velocityY = -10
    
    #Moves the sprite left/right
    #Parameter: x velocity of sprite
    def move(self, change):
        #Move sprite according to parameter
        self.velocityX = change
        
    #Shoots a bullet from the sprite
    #Parameter: velocity of bullet
    def shoot(self, bulletVelocity):
        #Creates a bullet if sprite has ammo
        if (self.ammo > 0):
            
            #Subtract 1 from ammo and create a bullet
            self.ammo -= 1
            
            #Check if it's an enemy or player bullet being fired
            if (self in self.currentLevel.enemies):
                bullet = Bullet(self, bulletVelocity, RED)
                self.currentLevel.enemyBullets.add(bullet)
            else:
                bullet = Bullet(self, bulletVelocity, PEAGREEN)
                self.currentLevel.playerBullets.add(bullet)
                
            #Add this bullet to the current level's all sprites list, so that it can be updated
            self.currentLevel.allSprites.add(bullet)
            
             
#-------------------------------------------------------------------------------
#Class for the player
class Player(MovingSprite):
    
    #ATTRIBUTES
    health      = None
    score       = None
    coins       = None
    playerImage = None
    indexWalk   = None
    walkImages  = None

    #Constructor method
    def __init__(self):
        #Call the parent MovingSprite Constructor
        super(Player, self).__init__()
        
        #Set the start position of the player
        self.rect.x = 150
        self.rect.y = 150

        #Load player images
        self.playerImage = importImage("images/player/defaultImage.png")
        self.walkImages  = [importImage("images/player/walkingImage1.png"), importImage("images/player/walkingImage2.png")]
        #self.walkImages.append(importImage("images/player/walkingImage1.png"))
        #self.walkImages.append(importImage("images/player/walkingImage2.png"))

        #Set the player's image
        self.image = self.playerImage
        self.image.set_colorkey(WHITE)

        #Set the initial walk image
        self.indexWalk = 0
        
        #Override default ammo of moving sprite class and set defualt ammo of player
        self.ammo = 20
        
        #Set the initial score, health and coins of the player
        self.score  =   0
        self.health = 100
        self.coins  =   0
    
    #Animates the player's walk     
    def walk(self):

        #If 15 frames have passed, change walk image
        if (self.velocityX != 0):
            self.image = self.walkImages[self.indexWalk]

            #If all images have been run through change the image back to the 1st
            if (self.indexWalk == 1):
                self.indexWalk = 0
            else:
                self.indexWalk += 1
               
                
#-------------------------------------------------------------------------------
#Template for an enemy
class Enemy(MovingSprite):
    #ATTRUBUTES
    jumpTime = None
    orgPos = None
    
    def __init__(self, pos):
        
        #Call the parent MovingSprite Constructor
        super(Enemy, self).__init__()
        
        #Set the enemy position based on parameter
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.orgPos = pos
        
        #Set the image of the enemy
        self.image = importImage("images/enemy.png")
        self.image.set_colorkey(WHITE)        
        
        #Give the enemy almost unlimited ammo (override default ammo)
        self.ammo = 2e64
        
        #Set the interval between jumps to random
        self.jumpTime = randint(45, 120)
    
    #Shoots the player (Overrided method)
    #Parameter: target to shoot (player)
    def shoot(self, target):
        
        #Check where the target it relative to this enemy, and fire in the direction of the target
        if (target.rect.x < self.rect.x):
            bulletVelocity = -15
        else:
            bulletVelocity = 15
            
        #Only shoot if the player is near the enemy
        if (abs(target.rect.x - self.rect.x) < 500 and abs(target.rect.y - self.rect.y) < 50):
            #Call the parent bullet method to shoot the bullet
            super(Enemy, self).shoot(bulletVelocity)
            
    #Makes the enemy jump (Overrided Method)
    #Parameter: target
    def jump(self, player):
        
        #Only jump if the player is near
        if (abs(player.rect.x - self.rect.x) < 700 and abs(player.rect.y - self.rect.y) < 400):
            super(Enemy, self).jump()
            

#-------------------------------------------------------------------------------
#Class for a platform
class Platform(pygame.sprite.Sprite):
    
    #Constructor Method
    #Parameters: position of platform, and dimensions of platform, and type of platform
    def __init__(self, pos, dimensions, imageType):
        
        super(Platform, self).__init__()
        
        #Set the dimensions of the plaform
        self.image = pygame.Surface(dimensions)
        
        #Set the position of the platform
        self.rect   = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        
        #Set the image of platform depending on type
        if (imageType == "platform"):
            self.image.blit(importImage("images/grassPlat.png"), [0,0])
        elif (imageType == "ground"):
            self.image.blit(importImage("images/grassGround.png"), [0,0])
        else:
            self.image.fill(BROWN)

        
#-------------------------------------------------------------------------------
#Class for an obstacle
class Obstacle(pygame.sprite.Sprite):
    
    #Constructor Method
    #Parameters: position, dimensions, and type
    def __init__(self, pos, dimensions, image):
        
        #Call the parent pygame constructor
        super(Obstacle, self).__init__()
        
        #Set the dimensions of the obstacle
        self.image = pygame.Surface(dimensions)
        
        #Set the position of the obstacle
        self.rect   = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        
        #Sets the image of the obstacle depending on type
        if (image == 'lava'):
            self.image.fill(LAVARED)
            
        
#-------------------------------------------------------------------------------
#Class for a level
class Level(object):
    #ATTRIBUTES
    platforms     = None
    coins         = None
    enemies       = None
    obstacles     = None
    allSprites    = None
    worldShift    = None
    maxWorldShift = None
    playerBullets = None
    enemyBullets  = None
    textList      = None
    #images       = None
    #backgroundImg = None
    
    #Constructor Method
    def __init__(self):
        
        #Initialize the Sprite lists
        self.collisionObjects = pygame.sprite.Group()
        self.enemies          = pygame.sprite.Group()
        self.allSprites       = pygame.sprite.Group()
        self.platforms        = pygame.sprite.Group()
        self.coins            = pygame.sprite.Group()
        self.playerBullets    = pygame.sprite.Group()
        self.enemyBullets     = pygame.sprite.Group()
        self.obstacles        = pygame.sprite.Group()
        
        #Control the world shift
        self.worldShift = 0 #This controls how much to shift the world
        self.maxWorldShift = 1000 # This is the world shift necessary for the level to end
        
        self.textList = []
        #self.images = []
     
    #Method to generate the platforms and enemies
    #Parameters: 2D list of platform info, 2D list of enemy positions, 2D list of coin positions, list of text box positions
    def generateLevel(self, platforms, enemies, coins, text, obstacles = []):
        
        #Iterate through the supplied platform information and create Platform objects
        for plat in platforms:
            platform = Platform([plat[0], plat[1]], [plat[2], plat[3]], plat[4])
            
            #Add the created platforms to the respective sprite lists
            self.platforms.add(platform)
            self.allSprites.add(platform)
            
        #Iterate through the supplied coin positions and create Coin objects
        for coinPos in coins:
            coin = Coin(coinPos)
            
            #Add the created coin to the respective sprite lists
            self.coins.add(coin)
            self.allSprites.add(coin)
        
        #Iterate through the supplied enemy position and create Enemy objects
        for enem in enemies:
            enemy = Enemy([enem[0], enem[1]])
            enemy.currentLevel = self
            
            #Add the created enemy to the respective sprite lists
            self.enemies.add(enemy)
            self.allSprites.add(enemy)

        #Iterate throught the supplied text box information and create text boxes
        for texts in text:
            self.textList.append(texts)
            
        #Iterate through the supplied image information and create images
        for obs in obstacles:
            obstacle = Obstacle([obs[0], obs[1]], [obs[2], obs[3]], obs[4])
            self.obstacles.add(obstacle)
            self.allSprites.add(obstacle)
    
    #Shifts the level (called when player approches right side of screen)
    #Parameters: Value to shift level
    def scroll(self, value):
        
        #Keep track of how much the level has been shifted
        self.worldShift += value
        
        #Shift all the platforms
        for sprite in self.platforms:
            sprite.rect.x += value
        
        #Shift all the coins
        for sprite in self.coins:
            sprite.rect.x += value
            
        #Shift the texts
        for texts in self.textList:
            texts[1] += value
        
        #Shift all of the obstacles
        for obs in self.obstacles:
            obs.rect.x += value
        
        #Shift all of the enemies
        for enem in self.enemies:
            enem.rect.x += value
        
    #Method to update all sprites and draw the level to the screen
    #Parameters: Screen to draw on
    def draw(self, screen):
        
        #Draw the background
        screen.fill(WHITE)
        
        #Draw the sprites
        self.allSprites.draw(screen)
        
        #Draw texts
        for texts in self.textList:
            text = font1.render(texts[0], True, BLACK)
            screen.blit(text, [texts[1], texts[2]])
       

#-------------------------------------------------------------------------------
#Class for a coin
class Coin(pygame.sprite.Sprite):
    #ATTRIBUTES
    image = None
    
    #Constructor Method
    #Parameters: position of coin
    def __init__(self, pos):
        
        #Call the parent pygame sprite constructor
        super(Coin, self).__init__()
        
        #Set the coin's size, graphic and position
        self.image = pygame.Surface([45, 50])
        self.image = importImage("images/coin.png")
        self.image.set_colorkey(WHITE)
        self.rect   = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        

#-------------------------------------------------------------------------------
#Class for a bullet
class Bullet(pygame.sprite.Sprite):
    
    #ATTRIBUTES
    velocityX = None
    image     = None
    
    #Constructor Method
    #Parameters: sprite who shoots bullet, algebraic speed of bullet, colour
    def __init__(self, shooter, velocityX, colour):
        
        #Call the parent pygame sprite constructor
        super(Bullet, self).__init__()
        
        #Create the Bullet image
        self.image = pygame.Surface([10, 10])
        self.rect  = self.image.get_rect()
        self.image.fill(colour)
        
        #Set the bullet's position to the shooter
        self.rect.x = shooter.rect.x 
        self.rect.y = shooter.rect.y
        
        #Set the x velocity based on parameter
        self.velocityX = velocityX
    
    #Updates the position of the bullet
    def update(self):
        
        #Move the bullet
        self.rect.x += self.velocityX
    

#-------------------------------------------------------------------------------
#Displays the HUD
def displayHud(level, health, coin, ammo, score, disHud, disLog, logLst):        
    
    #HUD
    #If player toggles HUD on, display HUD
    if (disHud == True):
        #HUD background
        pygame.draw.rect(screen, SKYBLUE, [0, 0, 1366, 50], 0)
        
        #Change colour of health box based on health remaining
        if (health <= 10):
            boxColour = RED
        elif (health <= 25):
            boxColour = ORANGE
        elif (health <= 50):
            boxColour = YELLOW
        else:
            boxColour = GREEN

        #Draw health bar based on health remaining
        if (health > 0):
            pygame.draw.rect(screen, boxColour, [235, 10, 2*health , 30], 0)   
        
        #Render text
        levelText  = font1.render('Level: ' + str(level), True, BLACK)
        healthText = font1.render('Health', True, BLACK)
        
        #Health bar displays a minimum of 0 health
        if (health < 0):
            healthNum = font1.render('0/100', True, BLACK)
        else:
            healthNum = font1.render(str(health) + '/100', True, BLACK)
        
        #Render all the text in the HUD
        coinsText = font1.render('Coins: x' + str(coin).zfill(3), True, BLACK)
        ammoText  = font1.render('Ammo: ' + str(ammo) + '/20'   , True, BLACK)
        scoreText = font1.render('Score: ' + str(score).zfill(6), True, BLACK)
        timeText  = font1.render('Time: ' + str(time).zfill(3)  , True, BLACK)
        
        #Display text
        screen.blit(levelText ,  [15, 15])
        screen.blit(healthText, [150, 15])
        screen.blit(healthNum , [300, 15])
        screen.blit(coinsText , [485, 15])
        screen.blit(ammoText  , [650, 15])
        screen.blit(scoreText , [815, 15])
        screen.blit(timeText  ,[1000, 15])

    #HELPER TEXT BOX/ LOG
    #If player toggles helper text on, display it
    if (disLog == True):
        pygame.draw.rect(screen, BLACK, [965, 50, 400, 155], 2)
        
        logPos = 190
        #Text in helper text box is only printed within box
        for i in range(-1, -len(logLst)-1, -1):
            
            #Render text
            bottom = font2.render(logLst[i], True, BLACK)
            #Display text 
            if (logPos >= 50):
                screen.blit(bottom, [970, logPos])
            logPos -= 15

            
#-------------------------------------------------------------------------------
#Imports an image
def importImage(path):
    
    try:
        image = pygame.image.load(path)
    except:
        image = None
        
    return image
    
    
#-------------------------------------------------------------------------------
#Ends the game and displays the ending screen
def displayEndScreen(screen, player, reason, time):

        #Fade background music out
        bgMusic.fadeout(500)
        
        #Check the reason for ending the game
        if (reason == 'lose'):   
            #Colour the screen red
            screenColour = RED
            
            #Make the time 0 so the player won't recieve time bonus
            time = 0
            player.health = 0
            
            #Render text
            msg = gameOverFont.render("Oh dear, you died!", True, WHITE)
            
        elif (reason == 'time'):
            #Colour the screen orange
            screenColour = ORANGE
            
            #Render text
            msg = gameOverFont.render("Looks like you're out of time!", True, WHITE)
            
            #Make the time  0 so player doesn't recieve time bonus
            time = 0
        
        else:   
            #Colour the screen green
            screenColour = PEAGREEN
            
            #Render text
            msg = gameOverFont.render("Yay! You Won!", True, WHITE)
        
        #Display text and colour screen based on result of game
        screen.fill(screenColour)
        if (reason == 'lose'):
            screen.blit(msg, [550, 350])
        elif (reason == 'time'):
            screen.blit(msg, [460, 350])
        else:
            screen.blit(msg, [600, 350])
        
        #Render the text to display score, and give player bonus score for remaining time and/or health
        score  = gameOverFont.render("Your score was: " + str(player.score+(time*50)+(player.health*75)), True, WHITE)
        bonusT = gameOverFont.render("Time bonus: " + str(time*50), True, WHITE)
        bonusH = gameOverFont.render("Health bonus: " + str(player.health*75), True, WHITE)
        screen.blit(score, [550, 450])
        screen.blit(bonusT, [550, 480])
        screen.blit(bonusH, [550, 510])
        
        
##########################################################################################################################################
'''
MAIN PROGRAM
'''
##########################################################################################################################################
if (__name__ == '__main__'):
    
    #Initialize pygame
    pygame.init()
    
    #Set time limit
    time = 180
    
    #Define fonts
    font1        = pygame.font.SysFont("Consolas", 20, False, False)
    font2        = pygame.font.SysFont("Consolas", 14, False, False)
    gameOverFont = pygame.font.SysFont("Consolas", 30, False, False)
    
    #Reference and configure sounds
    coinSound  = pygame.mixer.Sound("sounds/coin.ogg")
    coinSound.set_volume(0.05)
    playCoinSound = True
    bgMusic    = pygame.mixer.Sound("sounds/bgMusic.ogg")
    bgMusic.set_volume(0.25)
    bgMusic.play()
    jumpSound  = pygame.mixer.Sound("sounds/jump.ogg")
    shootSound = pygame.mixer.Sound("sounds/shoot.ogg")
    
    #Set the width and height of the screen [width, height]
    size   = (1366, 768)
    screen = pygame.display.set_mode(size)
    
    #Set the screen title and window icon
    pygame.display.set_caption("The Quest for the Golden Coins")
    iconSurface = importImage('images/coin.png')
    iconSurface.set_colorkey(BLACK)
    pygame.display.set_icon(iconSurface)
     
    #Main Loop Control
    done = False
     
    #Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    
    #List of levels
    allLevels = []

    #Generate the levels
    for i in range(2):
        
        #Check which level should be generated next, then make the level information
        #Specify first Level info
        if (i == 0):
            
            #Platform positions in format [x, y, width, height, type]
            platformInfo = [ [  700, 728, 1200,  50,   'ground'], 
                             [ 2450, 728,  550,  50,   'ground'], 
                             [ 3625, 728, 1375,  50,   'ground'],
                             [ 6500, 728, 1275,  50,   'ground'],
                             [ 9510, 728,  490,  50,   'ground'],
                             #----------------------------------
                             [ -350,   0,  350, 768,     'wall'], 
                             [    0, 268,  700, 500,   'ground'],
                             [ 1000, 628,  300,  50, 'platform'], 
                             [ 1450, 528,  300,  50, 'platform'],
                             [ 1900, 528,  550, 240,   'ground'],
                             #----------------------------------
                             [ 3175, 628,  300,  50, 'platform'],
                             [ 3650, 528, 1000,  50, 'platform'],
                             #----------------------------------
                             [ 5000, 678,  100, 100, 'platform'],
                             [ 5100, 628,  100, 150, 'platform'],
                             [ 5200, 578,  100, 200, 'platform'],
                             [ 5300, 528,  100, 250, 'platform'],
                             [ 5400, 478,  100, 300, 'platform'],
                             [ 5500, 428,  100, 350, 'platform'],
                             [ 5600, 378,  100, 400, 'platform'],
                             #----------------------------------
                             [ 5800, 378,  100, 400, 'platform'],
                             [ 5900, 428,  100, 350, 'platform'],
                             [ 6000, 478,  100, 300, 'platform'],
                             [ 6100, 528,  100, 250, 'platform'],
                             [ 6200, 578,  100, 200, 'platform'],
                             [ 6300, 628,  100, 150, 'platform'],
                             [ 6400, 678,  100, 100, 'platform'],
                             #----------------------------------
                             [ 6200, 378,  300,  50, 'platform'],
                             [ 6600, 268,  300,  50, 'platform'],
                             [ 7000, 628,  750,  20, 'platform'],
                             [ 7925, 528,  200,  50, 'platform'],
                             [ 8300, 428,  200,  50, 'platform'],
                             [ 8675, 328,  200,  50, 'platform'],
                             [ 8775, 678,  200,  50, 'platform'],
                             #----------------------------------
                             [ 9000, 678,  500, 100,   'ground'],
                             [ 8990, 563,  310,  50, 'platform'],
                             [ 9150, 448,  350,  50, 'platform'],
                             [ 9300, 333,  100,  50, 'platform'],
                             [ 9150, 303,  100,  50, 'platform'],
                             [ 9000, 273,  100,  50, 'platform'],
                             [ 9050, 158,  460,  50, 'platform'],
                             #----------------------------------
                             [ 8990, 158,   10, 405,     'wall'],
                             [ 9500, 208,   10, 615,     'wall'],
                             [ 9840,   0,  250, 600,     'wall'],
                             [10000,   0, 1500, 768,     'wall'] ]
            
            #Coin positions in format [x, y]                                      
            coinPos = [ [  780, 118], 
                        [  830, 148],
                        [  870, 188],
                        [ 1510, 675],
                        [ 1565, 675],
                        [ 1620, 675],
                        [ 1310, 520], 
                        [ 1350, 480],
                        [ 1400, 450],
                        #-----------
                        [ 2075, 378],
                        [ 2130, 378],
                        [ 2185, 378],
                        #-----------
                        [ 3035, 620],
                        [ 3075, 580],
                        [ 3125, 550],
                        [ 3510, 520],
                        [ 3550, 480],
                        [ 3600, 450],
                        [ 4700, 450],
                        [ 4750, 480],
                        [ 4790, 520],
                        #-----------
                        [ 5675, 258],
                        [ 5725, 228],
                        [ 5775, 258],
                        [ 6100, 370],
                        [ 6140, 330],
                        [ 6190, 300],
                        [ 6500, 260],
                        [ 6540, 220],
                        [ 6590, 190],
                        #-----------
                        [ 7270, 678],
                        [ 7320, 678],
                        [ 7370, 678],
                        [ 7420, 678],
                        [ 7470, 678],
                        #-----------
                        [ 7785, 520],
                        [ 7825, 480],
                        [ 7875, 450],
                        [ 8160, 420],
                        [ 8200, 380],
                        [ 8250, 350],
                        [ 8535, 320],
                        [ 8575, 280],
                        [ 8625, 250],
                        #-----------
                        [ 8930, 398], 
                        [ 8930, 448],
                        [ 8930, 488],
                        [ 9300, 508], 
                        [ 9340, 528],
                        [ 9380, 558],
                        [ 9060, 440], 
                        [ 9100, 400],
                        [ 9150, 370],
                        #-----------
                        [ 9630,  78],
                        [ 9680, 108],
                        [ 9720, 148], 
                        [ 9750, 198],
                        [ 9770, 258] ]
                        
            #Enemy positions in format [x, y]
            enemyPos = [ [ 2145, 468],
                         [ 3300, 568],
                         [ 4135, 468],
                         [ 5035, 618],
                         [ 5435, 418],
                         [ 6335, 318],
                         [ 6735, 208],
                         [ 8760, 268],
                         [ 9235, 618],
                         [ 9085, 503],
                         [ 9185, 503],
                         [ 9285, 388],
                         [ 9335, 273],
                         [ 9185, 243] ]
            
            #Obstacle positions in format [x, y, width, height, type]
            obstacles = [ [ 3000, 738,  625,  40, 'lava'],
                          [ 5700, 468,  100, 300, 'lava'],
                          [ 7775, 743, 1225,  50, 'lava'] ]
            
            #Text in format ["Text", x, y]          
            text = [ ["Press M for Help and Controls",  100,  75],
                     [">>>> Level 2 >>>>"            , 9800, 625],
                     [">>> This Way! >>>"            , 9800, 645],
                     ["Mind that LAVA! >>"           , 2770, 650] ] 
        
        #Specify second Level info
        else:
            platformInfo=[ [ -150,   0,  150,  768,     'wall'],
                           [ 1950,   0, 1500,  768,     'wall'],
                           [    0, 735,  600, 1950,   'ground'],
                           [  600, 620,  200,   50, 'platform'],
                           [  850, 550,  200,   50, 'platform'],
                           [ 1100, 480,  200,   50, 'platform'],
                           [ 1350, 410,  200,   50, 'platform'],
                           [ 1600, 750,  350,   75,   'ground'] ]
        
            coinPos = [ [  598, 575],
                        [  648, 575],
                        [  698, 575],
                        [  748, 575],
                        [  846, 495],
                        [  896, 495],
                        [  946, 495],
                        [  996, 495],
                        [ 1100, 425],
                        [ 1150, 425],
                        [ 1200, 425],
                        [ 1250, 425],
                        [ 1606, 700],
                        [ 1606, 645],
                        [ 1606, 590],
                        [ 1606, 535],
                        [ 1651, 700],
                        [ 1651, 645],
                        [ 1651, 590],
                        [ 1651, 535],
                        [ 1701, 700],
                        [ 1701, 645],
                        [ 1701, 590],
                        [ 1701, 535],
                        [ 1751, 700],
                        [ 1751, 645],
                        [ 1751, 590],
                        [ 1751, 535],
                        [ 1801, 700],
                        [ 1801, 645],
                        [ 1801, 590],
                        [ 1801, 535],
                        [ 1851, 700],
                        [ 1851, 645],
                        [ 1851, 590],
                        [ 1851, 535],
                        [ 1901, 700],
                        [ 1901, 645],
                        [ 1901, 590],
                        [ 1901, 535] ]
            
            enemyPos = [ [  688, 560],
                         [  934, 490],
                         [ 1180, 420],
                         [ 1438, 350] ]
                         
            obstacles = [ [600, 755, 1000, 75, 'lava'] ]  
                       
            text = [ ["WELCOME TO LEVEL 2! >>"     ,   25, 350],
                     [">>>>> Touch the wall >>>>>>", 1650, 350],
                     [">>>>>    TO WIN!!!   >>>>>>", 1650, 385] ]
            
        #Generate the level
        level = Level()
        level.generateLevel(platformInfo, enemyPos, coinPos, text, obstacles)
        allLevels.append(level)
        
    #Set the size of each level
    allLevels[0].maxWorldShift = 9970
    allLevels[1].maxWorldShift = 1920
    
    #Controls the index for the level list
    currentLevelNo = 0
    
    #Create the player and set his current level
    player = Player()
    player.currentLevel = allLevels[currentLevelNo]
    
    #List of player (Pygame cannot draw individual sprite)
    players = pygame.sprite.Group()
    players.add(player)
    
    #Controls whether to display HUD and helper text
    dispHud = True
    dispLog = False
    
    #Controls how to end the game
    playerWon = False
    outOfTime = False
    
    #--------------------------- MAIN PROGRAM LOOP -----------------------------
    while (not done): 
        
        #--------------------------- Event Processing --------------------------
        for event in pygame.event.get():
            
            #Check if user presses close
            if (event.type == pygame.QUIT):
              done = True
             
            #Check if user presses a key
            if (event.type == pygame.KEYDOWN):
                
                #Display help text in helper text box if user presses 1
                if (event.key == pygame.K_1):
                    #Add to the helper text list
                    LOGLST.append("Use arrow keys to move left/right.")
                    LOGLST.append("Press SPACE to jump.")
                    LOGLST.append("Press A to shoot left and D to shoot right.")
                    LOGLST.append("Press M to toggle log.")
                    LOGLST.append("Press N to toggle HUD.")
                    LOGLST.append("Press 3 to remove coin sound.")
                    
                #Toggle coin sound on/off if user presses 3
                if (event.key == pygame.K_3):
                    if (playCoinSound == True):
                        playCoinSound = False
                        LOGLST.append("You toggled coin sound off.") #Add to the helper text list
                    else:
                        playCoinSound = True
                        LOGLST.append("You toggled coin sound on.") #Add to the helper text list
                        
                #Player movement controls
                if (event.key == pygame.K_LEFT): #Move left
                    player.move(-6)
                if (event.key == pygame.K_RIGHT): #Move right
                    player.move(6)
                if (event.key == pygame.K_SPACE): #Jump
                    jumpSound.play()
                    player.jump()
                    
                #Player shooting controls
                if (event.key == pygame.K_a): #Shoot left
                    player.shoot(-15)
                    
                    #Check if the player has ammo, if so play sound
                    if (player.ammo > 0):
                        shootSound.play()
                    else:
                        LOGLST.append("You've run out of bullets!") #Add to the helper text list
                        
                if (event.key == pygame.K_d): #Shoot right
                    player.shoot(15)
                    
                    #Check if the player has ammo, if so play sound
                    if (player.ammo > 0):
                        shootSound.play()
                    else:
                        LOGLST.append("You've run out of bullets!") #Add to the helper text list
                        
                #Key to toggle HUD
                if (event.key == pygame.K_n):
                    if (dispHud == False):
                        dispHud = True
                    else:
                        dispHud = False
                        
                #Key to toggle Helper Text Box
                if (event.key == pygame.K_m):
                    if (dispLog == False):
                        dispLog = True
                    else:
                        dispLog = False
                
                '''
                ###Cheats for testing
                
                #Fly cheat 
                if (event.key == pygame.K_RETURN):
                    player.velocityY -= 10
                
                #Add health cheat 
                if (event.key == pygame.K_l):
                    player.health += 100
                    
                #Time cheat
                if (event.key == pygame.K_0):
                    time += 60
                if (event.key == pygame.K_9):
                    time -= 60
                    
                #Add score cheat
                if (event.key == pygame.K_8):
                    player.score += 500
                
                #Refill ammo cheat
                if (event.key == pygame.K_7):
                    player.ammo = 20
                '''
            
            #Make player stop when he releases the movement keys            
            if (event.type == pygame.KEYUP):
                #Set player velocity to 0 and reset sprite image to standing still image
                if ((event.key  ==  pygame.K_RIGHT and player.velocityX > 0) or (event.key == pygame.K_LEFT and player.velocityX < 0)):
                    player.move(0)
                    player.image = player.playerImage
                    
                #Reset sprite image to standing still image
                if (event.key == pygame.K_a or event.key == pygame.K_d):
                    player.image = player.playerImage


        #-------------------------- Game logic ---------------------------------
        grossPosition = player.rect.x - player.currentLevel.worldShift
        
        #-----COLLISIONS:
        
        #COINS:
        #Count the coins the player has collected
        coinList = pygame.sprite.spritecollide(player, player.currentLevel.coins, True)
        
        #Iterate through the coins the player collided with
        for coin in coinList:
            
            #Give the player points and play sound
            player.score += 100
            if (playCoinSound == True):
                coinSound.play()
            
            #Remove the collected coins from the sprite lists to prevent redrawing
            player.currentLevel.allSprites.remove(coin)
            player.currentLevel.coins.remove(coin)
            
            #Add 1 to the player's coins, and give him a small jump
            player.coins  += 1
            player.rect.y -= 10
        
        #OBSTACLES:
        #Count the deadly obstacles the player has collided with
        obsCollided = pygame.sprite.spritecollide(player, player.currentLevel.obstacles, False)
        
        #Iterate through the collided obstacles
        for obs in obsCollided:
            
            #Subtract 20 from health, and set player back before the obstacle
            player.health -= 20
            player.rect.x  = obs.rect.x - 200
            player.rect.y  = obs.rect.y - 200
            
            #Add to the helper text box
            LOGLST.append("You fell in lava! Be careful next time!") #Add to the helper text list
        
        #ENEMIES:
        #Count the enemies the player collided with
        enemiesCollided = pygame.sprite.spritecollide(player, player.currentLevel.enemies, True)
        
        #Iterate through the enemies the player collided with, subtract health, and set player back 5px
        for enem in enemiesCollided:
            
            player.rect.x -= 5
            player.health -= 20
            LOGLST.append("You ran into an enemy! How foolish!") #Add to the helper text list
            
        #BULLETS:
        #Iterate through the player's bullets
        for bull in player.currentLevel.playerBullets:
            
            #Count the bullets that hit an enemy
            bulletsCollidedEnem = pygame.sprite.spritecollide(bull, player.currentLevel.enemies, True)
            
            #Iterate through the bullets that hit an enemy-----
            for item in bulletsCollidedEnem:
                
                #Remove the bullet from the sprite lists, so that it won't be re-drawn
                player.currentLevel.playerBullets.remove(bull)
                player.currentLevel.allSprites.remove(bull)
                
                #Remove enemy and give player score
                player.currentLevel.playerBullets.remove(item)
                player.currentLevel.allSprites.remove(item)
                player.score += 250
                LOGLST.append("You shot an enemy!") #Add to the helper text list
            
            #Check if this bullet hit a platform
            bulletsCollidedPlats = pygame.sprite.spritecollide(bull, player.currentLevel.platforms, False)
            
            #Remove the bullet when it hits a platform
            for item in bulletsCollidedPlats:
                player.currentLevel.playerBullets.remove(bull)
                player.currentLevel.allSprites.remove(bull)
        
        #Iterate through all of the enemy bullets
        for bull in player.currentLevel.enemyBullets:
            
            #Count the bullets that hit a platform
            bulletsCollidedPlats = pygame.sprite.spritecollide(bull, player.currentLevel.platforms, False)
            
            #Delete all bullets that hit a platforms
            for item in bulletsCollidedPlats:
                
                player.currentLevel.enemyBullets.remove(bull)
                player.currentLevel.allSprites.remove(bull)
            
            #Count the enemy bullets that hit the player
            bulletsCollidedPlayer = pygame.sprite.spritecollide(player, player.currentLevel.enemyBullets, False)
            
            #Iterate through each enemy bullet that hits the player
            for bull in bulletsCollidedPlayer:
                
                #Remove the bullet from the sprite lists to prevent it from being re-drawn
                #and subtract 5 health for each bullet
                player.currentLevel.allSprites.remove(bull)
                player.currentLevel.enemyBullets.remove(bull)
                LOGLST.append("Oh no! An enemy shot you") #Add to the helper text list
                player.health -= 5

        #--- Level Management
        #Check if player has reached the right side of the screen, if so scroll level
        if (player.rect.x > 1000):
            distancePast  = 1000 - player.rect.x
            player.rect.x = 1000
            player.currentLevel.scroll(distancePast)
        
        #Check if the player has reached the left side of the screen, if so scroll level
        if (player.rect.x < 366):
            distancePast  = 366 - player.rect.x
            player.rect.x = 366
            player.currentLevel.scroll(distancePast)
            
        #Check if the player has reached the end of the level
        if (grossPosition >= player.currentLevel.maxWorldShift):
            
            #If the player is not on the last level, advance levels
            if (currentLevelNo == 1):
                playerWon = True
            else:
                #Change the variable that controls the level
                currentLevelNo += 1
                LOGLST.append("Player progressed to level 2!") #Add to the helper text list

                #Reset the player's position
                player.rect.x = 150
                player.rect.y = 150

                #If the player's ammo is less than 10, give the player 10 bullets, else refill ammo to 20 
                if (player.ammo < 10):
                    player.ammo += 10
                    LOGLST.append("Player receives 10 bullets.") #Add to the helper text list
                else:
                    player.ammo = 20
                    LOGLST.append("Player's bullets are replenished.") #Add to the helper text list
                  
                #Give player score and health  
                player.score  += 2500
                player.health += round((100-player.health)/3)
    
        #Set the player's current Level to the selected level
        player.currentLevel = allLevels[currentLevelNo]
        
        #--- More game logic
        #Walking animation every 15 frames
        if (player.currentFrame % 15 == 0):
            player.walk()
            
        #Make enemies shoot every 30 frames 
        if (player.currentFrame % 30 == 0):
            
            #Iterate through all the enemies in the level
            for enemy in player.currentLevel.enemies:
                enemy.shoot(player)
        
        #Every 60 frames (1 sec), subtract 1 from the time remaining
        if (player.currentFrame % 60 == 0 and player.health > 0 and not playerWon and time > 0):
            time -= 1
                
        #Make every enemy jump at their interval
        for enemy in player.currentLevel.enemies:
            
            #Check if this frame is the interval between jumps for this enemy
            if (player.currentFrame % enemy.jumpTime == 0):
                enemy.jump(player)

        #Update the position of the player, and all of the sprites in the current Level
        player.update()
        player.currentLevel.allSprites.update()
        
        #--------------------------- Drawing code ------------------------------
        
        #If the player dies, wins, or runs out of time, display the end screen
        #Otherwise, draw the level
        if (player.health <= 0):
            #Show end screen
            displayEndScreen(screen, player, 'lose', time)
            
            #Stop the player from moving
            player.rect.x = 50
            player.rect.y = 50
        
        elif (playerWon):
            #Show end screen
            displayEndScreen(screen, player, 'won', time)
            
            #Stop the player from moving
            player.rect.x = 50
            player.rect.y = 50
            
        elif (time <= 0):
            #Show end screen
            displayEndScreen(screen, player, 'time', time)
            
            #Stop the player from moving
            player.rect.x = 50
            player.rect.y = 50
            
        else:
            #Draw the level
            player.currentLevel.draw(screen)
            players.draw(screen)
            displayHud(currentLevelNo + 1, player.health, player.coins, player.ammo, player.score, dispHud, dispLog, LOGLST)
            
        #Console logging for debug purposes
        #print ("Pos: "+str(player.rect)+'\nGross: '+str(grossPosition)+'\nScore: '+str(player.score)+'\nAmmo: '+str(player.ammo)+'\nLevel: '+str(currentLevelNo+1)+'\nGross Pos: '+str(grossPosition))
        
        #----------------------- Update the screen -----------------------------
        
        #Update the screen
        pygame.display.flip()
        
        #Limit to 60 fps / 60 updates for second
        clock.tick(60)
    
    #Close the Window
    pygame.quit()
    
