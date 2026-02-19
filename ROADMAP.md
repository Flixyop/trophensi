# 🎯 ROADMAP TROPHÉES NSI - TROPHENSI

**Date de début :** Samedi 21 février 2026
**Date limite :** ~15 mars 2026 (3 semaines)
**Équipe :** 2 personnes (70% dev principal / 30% coéquipier)

---

## 📊 TEMPS DISPONIBLE

- **Semaine 1 (21-27 fév)** : 7 jours × 5-7h = **35-49h** (vacances)
- **Semaine 2 (28 fév-6 mars)** : 7 jours × 5-7h = **35-49h** (vacances)
- **Semaine 3 (7-13 mars)** : 1h mercredi + 4h week-end = **5h** (reprise cours)
- **TOTAL : ~75-103h de dev**

---

## 🎮 VISION DU JEU FINAL

**"Village Defense" - RTS Survie**
- Gérer un village attaqué par vagues de gobelins
- Recruter/placer des défenseurs (Warrior, Archer)
- Collecter ressources (bois, or)
- Construire bâtiments défensifs (Tours, Murs, Fermes)
- Survivre 10 vagues pour gagner

---

# 🚨 SEMAINE 1 : CORE GAMEPLAY (21-27 février)

## JOUR 1 - Samedi 21/02 - 5-7h - FONDATIONS SOLIDES

### Matin (2-3h) : Corrections critiques

#### 1. Bug directions
**Fichier : `direction.py`**
```python
# LIGNE 7-8 : Corriger bug directions
Left = (-1, 0)   # au lieu de (1, 0)
Right = (1, 0)   # au lieu de (-1, 0)
```

#### 2. Activer entités de test
**Fichier : `main.py`**
```python
# LIGNE 328-329 : Activer les entités pour tester
players = set([Player(i, i) for i in range(5)])  # 5 joueurs de base
goblins = set([Goblin(i, i) for i in range(30, 35)])  # 5 gobelins test
```

#### 3. Ajouter stats de combat
**Fichier : `entity.py`**
```python
# Ajouter après ligne 10 dans la classe Entity :
self.max_hp = 100
self.current_hp = 100
self.attack_damage = 10
self.attack_range = 1  # en tiles
self.last_attack_time = 0
self.attack_cooldown = 1.0  # secondes
```

---

### Après-midi (3-4h) : Système de ressources

#### 1. Créer ResourceManager
**Créer nouveau fichier : `resources.py`**
```python
class ResourceManager:
    def __init__(self):
        self.wood = 100
        self.gold = 100
        self.food = 50
        self.max_population = 20
        self.current_population = 5

    def can_afford(self, wood_cost, gold_cost):
        return self.wood >= wood_cost and self.gold >= gold_cost

    def spend(self, wood_cost, gold_cost):
        if self.can_afford(wood_cost, gold_cost):
            self.wood -= wood_cost
            self.gold -= gold_cost
            return True
        return False

    def add(self, wood=0, gold=0):
        self.wood += wood
        self.gold += gold
```

#### 2. Intégrer dans Game
**Fichier : `main.py` dans `__init__` de Game (ligne ~40)**
```python
# Ajouter après self.camera :
from resources import ResourceManager
self.resources = ResourceManager()
self.gold_timer = 0  # Pour génération automatique
```

#### 3. Génération automatique d'or
**Fichier : `main.py` dans `update()` (ligne ~163)**
```python
# Ajouter avant camera.update() :
dt = self.clock.get_time() / 1000.0  # delta time en secondes
self.gold_timer += dt
if self.gold_timer >= 2.0:  # +1 gold toutes les 2 secondes
    self.resources.add(gold=1)
    self.gold_timer = 0
```

#### 4. Affichage ressources
**Fichier : `main.py` dans `draw()` (ligne ~137)**
```python
# Ajouter après self.draw_entities() :
self.draw_resources()
```

**Fichier : `main.py` - Ajouter nouvelle méthode après `draw_entities()` :**
```python
def draw_resources(self):
    font = pygame.font.Font(None, 36)
    # Afficher or
    gold_text = font.render(f"Gold: {self.resources.gold}", True, (255, 215, 0))
    self.screen.blit(gold_text, (10, 10))
    # Afficher bois
    wood_text = font.render(f"Wood: {self.resources.wood}", True, (139, 69, 19))
    self.screen.blit(wood_text, (10, 50))
    # Afficher population
    pop_text = font.render(f"Pop: {self.resources.current_population}/{self.resources.max_population}", True, (255, 255, 255))
    self.screen.blit(pop_text, (10, 90))
```

**✅ FIN JOUR 1 : Ressources visibles qui augmentent automatiquement**

---

## JOUR 2 - Dimanche 22/02 - 5-7h - SÉLECTION D'UNITÉS

### Matin (3h) : Système de sélection

#### 1. Créer SelectionManager
**Créer nouveau fichier : `selection.py`**
```python
import pygame
from utils import PIXEL_SIZE

class SelectionManager:
    def __init__(self):
        self.selected_units = set()

    def clear(self):
        self.selected_units.clear()

    def add_unit(self, unit):
        self.selected_units.add(unit)

    def remove_unit(self, unit):
        if unit in self.selected_units:
            self.selected_units.remove(unit)

    def get_unit_at_position(self, world_x, world_y, entities):
        """Trouve l'unité aux coordonnées monde"""
        for entity in entities:
            if entity.x == world_x and entity.y == world_y:
                return entity
        return None

    def get_units_in_rect(self, rect, entities):
        """Trouve toutes les unités dans un rectangle (coordonnées monde)"""
        units = []
        for entity in entities:
            entity_world_x = entity.x * PIXEL_SIZE
            entity_world_y = entity.y * PIXEL_SIZE
            if rect.collidepoint(entity_world_x, entity_world_y):
                units.append(entity)
        return units

    def is_selected(self, unit):
        return unit in self.selected_units
```

#### 2. Intégrer SelectionManager
**Fichier : `main.py` dans `__init__` après resources :**
```python
from selection import SelectionManager
self.selection = SelectionManager()
```

#### 3. Gestion clic gauche (sélection)
**Fichier : `main.py` dans `event()` - MODIFIER le bloc MOUSEBUTTONDOWN (ligne ~153) :**
```python
elif event.type == pygame.MOUSEBUTTONDOWN:
    if event.button == 1:  # Clic gauche = sélection
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Convertir coordonnées écran vers monde
        world_x = (mouse_x + self.camera.x) // PIXEL_SIZE
        world_y = (mouse_y + self.camera.y) // PIXEL_SIZE

        # Chercher unité à cette position
        unit = self.selection.get_unit_at_position(world_x, world_y, self.entities.players)

        if unit:
            # Shift = ajouter à sélection, sinon remplacer
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_LSHIFT]:
                self.selection.clear()
            self.selection.add_unit(unit)
        else:
            self.selection.clear()

    elif event.button == 3:  # Clic droit = zone sélection
        self.selection_start_point = pygame.mouse.get_pos()
        self.is_user_selecting = True
```

#### 4. Gestion clic droit relâché (zone sélection)
**Fichier : `main.py` dans `event()` - MODIFIER le bloc MOUSEBUTTONUP (ligne ~157) :**
```python
elif event.type == pygame.MOUSEBUTTONUP:
    if event.button == 3:
        if self.is_user_selecting:
            # Calculer rectangle de sélection en coordonnées monde
            start_world_x = self.selection_start_point[0] + self.camera.x
            start_world_y = self.selection_start_point[1] + self.camera.y

            mouse_x, mouse_y = pygame.mouse.get_pos()
            end_world_x = mouse_x + self.camera.x
            end_world_y = mouse_y + self.camera.y

            # Créer rect
            x = min(start_world_x, end_world_x)
            y = min(start_world_y, end_world_y)
            w = abs(end_world_x - start_world_x)
            h = abs(end_world_y - start_world_y)

            select_rect = pygame.Rect(x, y, w, h)

            # Sélectionner unités dans rect
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_LSHIFT]:
                self.selection.clear()

            units = self.selection.get_units_in_rect(select_rect, self.entities.players)
            for unit in units:
                self.selection.add_unit(unit)

        self.selection_start_point = (0, 0)
        self.is_user_selecting = False
```

---

### Après-midi (2-4h) : Affichage visuel sélection

#### 1. Bordure verte pour unités sélectionnées
**Fichier : `main.py` dans `draw_entities()` - REMPLACER (ligne ~180) :**
```python
def draw_entities(self):
    for player in self.entities.players:
        self.draw_image("player", player.x, player.y)

        # Si sélectionné, bordure verte
        if self.selection.is_selected(player):
            pos_screen_x = (player.x * PIXEL_SIZE) - self.camera.x
            pos_screen_y = (player.y * PIXEL_SIZE) - self.camera.y
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (pos_screen_x, pos_screen_y, PIXEL_SIZE, PIXEL_SIZE), 3)

    for goblin in self.entities.goblins:
        self.draw_image("goblin", goblin.x, goblin.y)
```

**✅ FIN JOUR 2 : Sélection d'unités fonctionnelle avec feedback visuel**

---

## JOUR 3 - Lundi 23/02 - 5-7h - DÉPLACEMENT PAR CLIC

### Matin (3h) : États et cibles

#### 1. Ajouter système d'états
**Fichier : `entity.py` - Modifier classe Entity (ligne ~6) :**
```python
class Entity:
    def __init__(self, x, y):
        self.img = "default"
        self.x = x
        self.y = y

        # Stats combat (ajouté Jour 1)
        self.max_hp = 100
        self.current_hp = 100
        self.attack_damage = 10
        self.attack_range = 1
        self.last_attack_time = 0
        self.attack_cooldown = 1.0

        # NOUVEAU - États
        self.state = "IDLE"  # IDLE, MOVING, ATTACKING
        self.target_x = None
        self.target_y = None
        self.move_speed = 0.3  # tiles par update (ajuster selon vitesse voulue)

    def set_move_target(self, target_x, target_y):
        """Donner ordre de déplacement"""
        self.target_x = target_x
        self.target_y = target_y
        self.state = "MOVING"

    def update_movement(self):
        """Appelé chaque frame pour bouger vers la cible"""
        if self.state != "MOVING" or self.target_x is None:
            return

        # Calculer direction vers cible
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        # Distance Manhattan
        distance = abs(dx) + abs(dy)

        if distance < 0.5:  # Arrivé à destination
            self.x = self.target_x
            self.y = self.target_y
            self.target_x = None
            self.target_y = None
            self.state = "IDLE"
            return

        # Se déplacer dans la bonne direction
        if abs(dx) > abs(dy):
            # Bouger horizontalement
            if dx > 0:
                self.move(Direction.Right)
            else:
                self.move(Direction.Left)
        else:
            # Bouger verticalement
            if dy > 0:
                self.move(Direction.Down)
            else:
                self.move(Direction.Up)

    def move(self, dir: Direction):
        dir_val = dir.value
        self.x = (self.x + dir_val[0]) % BOARD_SIZE[0]
        self.y = (self.y + dir_val[1]) % BOARD_SIZE[1]
```

---

### Après-midi (2-4h) : Ordres de mouvement

#### 1. Gestion clic droit pour ordre de déplacement
**Fichier : `main.py` dans `event()` - MODIFIER le bloc clic droit MOUSEBUTTONDOWN :**
```python
elif event.button == 3:  # Clic droit
    # Vérifier si c'est un ordre de mouvement ou début de sélection
    if len(self.selection.selected_units) > 0:
        # Ordre de mouvement immédiat
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_world_x = (mouse_x + self.camera.x) // PIXEL_SIZE
        target_world_y = (mouse_y + self.camera.y) // PIXEL_SIZE

        # Donner ordre à toutes les unités sélectionnées
        for unit in self.selection.selected_units:
            unit.set_move_target(target_world_x, target_world_y)
    else:
        # Sinon c'est le début d'une zone de sélection
        self.selection_start_point = pygame.mouse.get_pos()
        self.is_user_selecting = True
```

#### 2. Update loop pour mouvement
**Fichier : `main.py` - MODIFIER la méthode `move()` (ligne ~224) :**
```python
def move(self):
    # Update mouvement des players (contrôlés par joueur)
    for player in self.entities.players:
        player.update_movement()

    # Gobelins : mouvement IA (garde l'ancien comportement pour l'instant)
    for goblin in self.entities.goblins:
        goblin.move(self.entities.players)

        target = next(
            (p for p in self.entities.players if p.x == goblin.x and p.y == goblin.y),
            None,
        )

        if target is not None:
            self.entities.players.remove(target)
```

**✅ FIN JOUR 3 : Unités se déplacent où on clique !**

---

## JOUR 4 - Mardi 24/02 - 5-7h - COMBAT FONCTIONNEL

### Matin (3h) : Barres de vie

#### 1. Afficher barres de vie sur entités
**Fichier : `main.py` - Modifier `draw_entities()` (ligne ~180) :**
```python
def draw_entities(self):
    for player in self.entities.players:
        self.draw_image("player", player.x, player.y)

        # Bordure si sélectionné
        if self.selection.is_selected(player):
            pos_screen_x = (player.x * PIXEL_SIZE) - self.camera.x
            pos_screen_y = (player.y * PIXEL_SIZE) - self.camera.y
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (pos_screen_x, pos_screen_y, PIXEL_SIZE, PIXEL_SIZE), 3)

        # NOUVEAU - Barre de vie
        self.draw_healthbar(player)

    for goblin in self.entities.goblins:
        self.draw_image("goblin", goblin.x, goblin.y)
        self.draw_healthbar(goblin)
```

#### 2. Méthode draw_healthbar
**Fichier : `main.py` - Ajouter nouvelle méthode après `draw_entities()` :**
```python
def draw_healthbar(self, entity):
    """Dessine barre de vie au-dessus d'une entité"""
    bar_width = PIXEL_SIZE
    bar_height = 5

    pos_screen_x = (entity.x * PIXEL_SIZE) - self.camera.x
    pos_screen_y = (entity.y * PIXEL_SIZE) - self.camera.y - 10  # Au-dessus

    # Fond rouge
    pygame.draw.rect(self.screen, (255, 0, 0),
                    (pos_screen_x, pos_screen_y, bar_width, bar_height))

    # Barre verte (proportionnelle aux HP)
    hp_percent = entity.current_hp / entity.max_hp
    green_width = int(bar_width * hp_percent)
    pygame.draw.rect(self.screen, (0, 255, 0),
                    (pos_screen_x, pos_screen_y, green_width, bar_height))
```

---

### Après-midi (2-4h) : Système de combat

#### 1. Méthodes de combat dans Entity
**Fichier : `entity.py` - Ajouter méthodes dans Entity :**
```python
def get_enemy_in_range(self, enemies):
    """Trouve l'ennemi le plus proche à portée"""
    closest_enemy = None
    min_distance = self.attack_range + 1

    for enemy in enemies:
        distance = abs(enemy.x - self.x) + abs(enemy.y - self.y)  # Manhattan
        if distance <= self.attack_range and distance < min_distance:
            closest_enemy = enemy
            min_distance = distance

    return closest_enemy

def attack(self, target, current_time):
    """Attaquer une cible si cooldown OK"""
    if current_time - self.last_attack_time >= self.attack_cooldown:
        target.take_damage(self.attack_damage)
        self.last_attack_time = current_time
        return True
    return False

def take_damage(self, damage):
    """Prendre des dégâts"""
    self.current_hp -= damage
    if self.current_hp < 0:
        self.current_hp = 0

def is_dead(self):
    return self.current_hp <= 0
```

#### 2. Intégrer combat dans game loop
**Fichier : `main.py` - Modifier méthode `move()` (ligne ~224) :**
```python
def move(self):
    import time
    current_time = time.time()

    # Players : mouvement + combat
    for player in self.entities.players:
        # Chercher ennemi à portée
        enemy = player.get_enemy_in_range(self.entities.goblins)

        if enemy:
            # Attaquer si possible
            player.state = "ATTACKING"
            player.attack(enemy, current_time)
        else:
            # Sinon bouger
            if player.state != "MOVING":
                player.state = "IDLE"
            player.update_movement()

    # Gobelins : mouvement IA + combat
    for goblin in self.entities.goblins:
        # Chercher player à portée
        target = goblin.get_enemy_in_range(self.entities.players)

        if target:
            goblin.attack(target, current_time)
        else:
            # Sinon bouger vers players
            goblin.move(self.entities.players)

    # Supprimer morts
    self.entities.players = set(p for p in self.entities.players if not p.is_dead())
    self.entities.goblins = set(g for g in self.entities.goblins if not g.is_dead())
```

**✅ FIN JOUR 4 : Combat fonctionne, barres de vie, unités meurent**

---

## JOUR 5 - Mercredi 25/02 - 5-7h - SYSTÈME DE VAGUES

### Objectif : Vagues d'ennemis progressives

#### 1. Créer WaveManager
**Créer fichier : `wave_manager.py`**
```python
import random
from entity import Goblin
from utils import WORLD_WIDTH, WORLD_HEIGHT

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.is_wave_active = False
        self.time_until_next_wave = 30.0  # 30 secondes entre vagues
        self.enemies_remaining = 0

    def update(self, dt):
        """dt = delta time en secondes"""
        if not self.is_wave_active:
            self.time_until_next_wave -= dt
            if self.time_until_next_wave <= 0:
                return True  # Lancer nouvelle vague
        return False

    def start_wave(self):
        """Démarre une nouvelle vague"""
        self.current_wave += 1
        self.is_wave_active = True
        self.time_until_next_wave = 30.0

        # Calculer nombre d'ennemis
        num_enemies = 5 + (self.current_wave - 1) * 3
        return num_enemies

    def spawn_enemies(self, num_enemies):
        """Crée les gobelins aux bords de la map"""
        goblins = set()

        for i in range(num_enemies):
            # Spawn aléatoire sur les bords
            side = random.choice(['top', 'bottom', 'left', 'right'])

            if side == 'top':
                x = random.randint(0, WORLD_WIDTH - 1)
                y = 0
            elif side == 'bottom':
                x = random.randint(0, WORLD_WIDTH - 1)
                y = WORLD_HEIGHT - 1
            elif side == 'left':
                x = 0
                y = random.randint(0, WORLD_HEIGHT - 1)
            else:  # right
                x = WORLD_WIDTH - 1
                y = random.randint(0, WORLD_HEIGHT - 1)

            goblins.add(Goblin(x, y))

        return goblins

    def check_wave_complete(self, num_enemies_alive):
        """Vérifie si vague terminée"""
        if self.is_wave_active and num_enemies_alive == 0:
            self.is_wave_active = False
            return True
        return False
```

#### 2. Intégrer WaveManager
**Fichier : `main.py` dans `__init__` après selection :**
```python
from wave_manager import WaveManager
self.wave_manager = WaveManager()
```

#### 3. Retirer gobelins initiaux
**Fichier : `main.py` - Modifier `__init__` (ligne ~328) :**
```python
players = set([Player(i, i) for i in range(5)])
goblins = set()  # Vide au départ, spawn par vagues
```

#### 4. Update avec gestion vagues
**Fichier : `main.py` dans `update()` après la ligne camera.update() :**
```python
def update(self):
    dt = self.clock.get_time() / 1000.0  # delta time

    # Gold automatique
    self.gold_timer += dt
    if self.gold_timer >= 2.0:
        self.resources.add(gold=1)
        self.gold_timer = 0

    # NOUVEAU - Gestion vagues
    if self.wave_manager.update(dt):
        # Lancer nouvelle vague
        num_enemies = self.wave_manager.start_wave()
        new_goblins = self.wave_manager.spawn_enemies(num_enemies)
        self.entities.goblins.update(new_goblins)

    # Vérifier si vague terminée
    if self.wave_manager.check_wave_complete(len(self.entities.goblins)):
        print(f"Vague {self.wave_manager.current_wave} terminée !")

    self.camera.update()
    pygame.display.flip()
```

#### 5. Affichage info vague
**Fichier : `main.py` - Modifier `draw_resources()` :**
```python
def draw_resources(self):
    font = pygame.font.Font(None, 36)

    gold_text = font.render(f"Gold: {self.resources.gold}", True, (255, 215, 0))
    self.screen.blit(gold_text, (10, 10))

    wood_text = font.render(f"Wood: {self.resources.wood}", True, (139, 69, 19))
    self.screen.blit(wood_text, (10, 50))

    pop_text = font.render(f"Pop: {self.resources.current_population}/{self.resources.max_population}", True, (255, 255, 255))
    self.screen.blit(pop_text, (10, 90))

    # NOUVEAU - Info vague
    wave_text = font.render(f"Vague: {self.wave_manager.current_wave}/10", True, (255, 100, 100))
    self.screen.blit(wave_text, (10, 130))

    if not self.wave_manager.is_wave_active:
        timer_text = font.render(f"Prochaine vague: {int(self.wave_manager.time_until_next_wave)}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 170))
```

**✅ FIN JOUR 5 : Système de vagues automatique fonctionnel**

---

## JOUR 6 - Jeudi 26/02 - 5-7h - WIN/LOSE & RECRUTEMENT

### Matin (2-3h) : Conditions victoire/défaite

#### 1. Ajouter HP village et game state
**Fichier : `main.py` dans `__init__` après wave_manager :**
```python
# NOUVEAU - Village HP
self.village_hp = 100
self.village_max_hp = 100
self.game_state = "PLAYING"  # PLAYING, WON, LOST
```

#### 2. Goblin attaque village
**Fichier : `main.py` dans `move()` - Modifier section gobelins :**
```python
# Dans la boucle gobelins, après goblin.move() :
for goblin in list(self.entities.goblins):  # list() pour éviter erreur modification pendant iteration
    target = goblin.get_enemy_in_range(self.entities.players)

    if target:
        goblin.attack(target, current_time)
    else:
        goblin.move(self.entities.players)

        # NOUVEAU - Vérifier si goblin touche village
        v_start_x = self.village_pos_x // PIXEL_SIZE
        v_start_y = self.village_pos_y // PIXEL_SIZE
        v_end_x = v_start_x + (self.assets["village_map"].get_width() // PIXEL_SIZE)
        v_end_y = v_start_y + (self.assets["village_map"].get_height() // PIXEL_SIZE)

        if (goblin.x >= v_start_x and goblin.x < v_end_x and
            goblin.y >= v_start_y and goblin.y < v_end_y):
            self.village_hp -= 10
            self.entities.goblins.remove(goblin)
            print(f"Village touché ! HP: {self.village_hp}")
```

#### 3. Check win/lose
**Fichier : `main.py` dans `update()` après wave check :**
```python
# NOUVEAU - Check win/lose
if self.village_hp <= 0:
    self.game_state = "LOST"
    print("GAME OVER - Village détruit !")

if self.wave_manager.current_wave >= 10 and not self.wave_manager.is_wave_active and len(self.entities.goblins) == 0:
    self.game_state = "WON"
    print("VICTOIRE - 10 vagues survécues !")
```

#### 4. Afficher HP village
**Fichier : `main.py` - Modifier `draw_resources()` :**
```python
# Ajouter après pop_text :
village_hp_text = font.render(f"Village: {self.village_hp}/{self.village_max_hp} HP", True, (255, 50, 50))
self.screen.blit(village_hp_text, (SCREEN_SIZE[0] - 300, 10))
```

---

### Après-midi (3-4h) : Recrutement basique

#### 1. Créer classe Archer
**Fichier : `entity.py` - Modifier classes Player et ajouter Archer :**
```python
class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_hp = 80
        self.current_hp = 80
        self.attack_damage = 15
        self.attack_range = 1

class Archer(Entity):  # NOUVELLE CLASSE
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "player"  # Même sprite pour l'instant
        self.max_hp = 50
        self.current_hp = 50
        self.attack_damage = 12
        self.attack_range = 3  # Portée longue !
```

#### 2. Touches de recrutement
**Fichier : `main.py` dans `event()` - Ajouter gestion touches clavier :**
```python
elif event.type == pygame.KEYDOWN:
    if event.key == pygame.K_q:  # Q = Recruter Warrior
        if self.resources.spend(wood=0, gold=20):
            # Spawn près du village
            v_x = self.village_pos_x // PIXEL_SIZE + 10
            v_y = self.village_pos_y // PIXEL_SIZE + 10

            from entity import Player
            new_unit = Player(v_x, v_y)
            self.entities.players.add(new_unit)
            self.resources.current_population += 1
            print("Warrior recruté !")

    elif event.key == pygame.K_w:  # W = Recruter Archer
        if self.resources.spend(wood=0, gold=30):
            v_x = self.village_pos_x // PIXEL_SIZE + 15
            v_y = self.village_pos_y // PIXEL_SIZE + 10

            from entity import Archer
            new_unit = Archer(v_x, v_y)
            self.entities.players.add(new_unit)
            self.resources.current_population += 1
            print("Archer recruté !")
```

#### 3. Afficher aide touches
**Fichier : `main.py` - Modifier `draw_resources()` pour afficher touches :**
```python
# Ajouter en bas à droite :
small_font = pygame.font.Font(None, 24)
help_text1 = small_font.render("Q: Warrior (20g)", True, (200, 200, 200))
help_text2 = small_font.render("W: Archer (30g)", True, (200, 200, 200))
self.screen.blit(help_text1, (SCREEN_SIZE[0] - 200, SCREEN_SIZE[1] - 80))
self.screen.blit(help_text2, (SCREEN_SIZE[0] - 200, SCREEN_SIZE[1] - 50))
```

**✅ FIN JOUR 6 : Win/Lose + Recrutement par touches Q/W**

---

## JOUR 7 - Vendredi 27/02 - 5-7h - POLISH & TESTS

### Objectif : Équilibrer et corriger bugs

#### Toute la journée (5-7h)

1. **Jouer 10 parties complètes**
   - Noter tous les bugs dans un fichier BUGS.txt
   - Est-ce trop facile/dur ?
   - Les ressources sont équilibrées ?
   - Arriver à la vague 10 est possible ?

2. **Ajustements probables :**
   - HP village trop faible ? → Augmenter à 200
   - Pas assez d'or ? → Augmenter génération à +2 gold/2sec
   - Archers trop forts ? → Réduire portée à 2 ou dégâts à 8
   - Gobelins trop nombreux ? → Ajuster formule vague (3 → 2 par vague)
   - Vagues trop rapprochées ? → Augmenter délai à 45 secondes

3. **Corrections bugs critiques**
   - Priorité 1 : Crashes
   - Priorité 2 : Unités qui se bloquent
   - Priorité 3 : Balance gameplay

4. **Ajouter écran Game Over/Victory**

**Fichier : `main.py` - Modifier méthode `draw()` :**
```python
def draw(self):
    self.screen.fill((255, 255, 255))

    if self.game_state == "PLAYING":
        self.draw_map()
        self.draw_entities()
        self.draw_screen_selection()
        self.draw_resources()

    elif self.game_state == "WON":
        # Afficher fond + map en arrière-plan
        self.draw_map()

        # Overlay semi-transparent
        overlay = pygame.Surface(SCREEN_SIZE)
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Texte victoire
        font = pygame.font.Font(None, 72)
        text = font.render("VICTOIRE !", True, (0, 255, 0))
        rect = text.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 - 50))
        self.screen.blit(text, rect)

        # Stats
        small_font = pygame.font.Font(None, 36)
        stats = small_font.render(f"10 vagues survécues - Village: {self.village_hp}/{self.village_max_hp} HP", True, (255, 255, 255))
        stats_rect = stats.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 + 20))
        self.screen.blit(stats, stats_rect)

    elif self.game_state == "LOST":
        # Afficher fond + map en arrière-plan
        self.draw_map()

        # Overlay semi-transparent
        overlay = pygame.Surface(SCREEN_SIZE)
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Texte défaite
        font = pygame.font.Font(None, 72)
        text = font.render("DEFAITE...", True, (255, 0, 0))
        rect = text.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 - 50))
        self.screen.blit(text, rect)

        # Stats
        small_font = pygame.font.Font(None, 36)
        stats = small_font.render(f"Vague {self.wave_manager.current_wave} atteinte", True, (255, 255, 255))
        stats_rect = stats.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 + 20))
        self.screen.blit(stats, stats_rect)
```

**✅ FIN SEMAINE 1 : JEU MINIMAL JOUABLE ! 🎉**

**Features complétées :**
- ✅ Sélection d'unités (clic gauche + zone)
- ✅ Déplacement par clic droit
- ✅ Combat avec barres de vie
- ✅ Système de vagues progressif
- ✅ Ressources (gold auto)
- ✅ Recrutement (Warrior, Archer)
- ✅ Win/Lose conditions
- ✅ Écrans fin de partie

---

# 🎨 SEMAINE 2 : CONTENU + POLISH (28 fév - 6 mars)

## JOUR 8 - Samedi 28/02 - 5-7h - UI PROFESSIONNELLE

### Objectif : Interface propre et fonctionnelle

### Matin (3h) : Panels et tooltips

#### 1. Créer UIManager
**Créer fichier : `ui_manager.py`**
```python
import pygame

class UIButton:
    def __init__(self, x, y, width, height, text, cost_gold=0, cost_wood=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.cost_gold = cost_gold
        self.cost_wood = cost_wood
        self.hovered = False

    def draw(self, screen, resources):
        # Couleur selon si on peut acheter
        can_afford = resources.can_afford(self.cost_wood, self.cost_gold)

        if self.hovered:
            color = (100, 100, 255) if can_afford else (150, 50, 50)
        else:
            color = (70, 70, 200) if can_afford else (100, 50, 50)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # Bordure

        # Texte
        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

        # Afficher tooltip si hover
        if self.hovered:
            self.draw_tooltip(screen)

    def draw_tooltip(self, screen):
        tooltip_text = f"Coût: {self.cost_gold}g"
        if self.cost_wood > 0:
            tooltip_text += f" {self.cost_wood}w"

        font = pygame.font.Font(None, 20)
        tooltip_surf = font.render(tooltip_text, True, (255, 255, 255))
        tooltip_rect = tooltip_surf.get_rect()
        tooltip_rect.topleft = (self.rect.x, self.rect.y - 25)

        # Fond tooltip
        bg_rect = tooltip_rect.inflate(10, 5)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1)
        screen.blit(tooltip_surf, tooltip_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Création des boutons
        button_y = screen_height - 60
        self.buttons = {
            'warrior': UIButton(10, button_y, 120, 50, "Warrior (Q)", cost_gold=20),
            'archer': UIButton(140, button_y, 120, 50, "Archer (W)", cost_gold=30),
            'tower': UIButton(270, button_y, 120, 50, "Tour (E)", cost_gold=50, cost_wood=30),
            'wall': UIButton(400, button_y, 120, 50, "Mur (R)", cost_wood=20),
        }

    def update(self, mouse_pos):
        for button in self.buttons.values():
            button.update(mouse_pos)

    def draw(self, screen, resources):
        # Panel en bas
        panel_rect = pygame.Rect(0, self.screen_height - 70, self.screen_width, 70)
        pygame.draw.rect(screen, (40, 40, 40), panel_rect)
        pygame.draw.rect(screen, (100, 100, 100), panel_rect, 2)

        # Boutons
        for button in self.buttons.values():
            button.draw(screen, resources)

    def handle_click(self, mouse_pos):
        """Retourne le nom du bouton cliqué, ou None"""
        for name, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                return name
        return None
```

#### 2. Intégrer UIManager
**Fichier : `main.py` dans `__init__` :**
```python
from ui_manager import UIManager
self.ui_manager = UIManager(SCREEN_SIZE[0], SCREEN_SIZE[1])
```

#### 3. Dessiner UI
**Fichier : `main.py` dans `draw()` section PLAYING :**
```python
if self.game_state == "PLAYING":
    self.draw_map()
    self.draw_entities()
    self.draw_screen_selection()
    self.draw_resources()
    self.ui_manager.draw(self.screen, self.resources)  # NOUVEAU
```

#### 4. Update UI (hover)
**Fichier : `main.py` dans `update()` :**
```python
# Après camera.update() :
mouse_pos = pygame.mouse.get_pos()
self.ui_manager.update(mouse_pos)
```

#### 5. Gérer clics sur boutons
**Fichier : `main.py` dans `event()` - Modifier MOUSEBUTTONDOWN bouton 1 :**
```python
if event.button == 1:  # Clic gauche
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Vérifier si clic sur UI
    button_clicked = self.ui_manager.handle_click((mouse_x, mouse_y))

    if button_clicked == 'warrior':
        if self.resources.spend(wood=0, gold=20):
            v_x = self.village_pos_x // PIXEL_SIZE + 10
            v_y = self.village_pos_y // PIXEL_SIZE + 10
            from entity import Player
            self.entities.players.add(Player(v_x, v_y))
            self.resources.current_population += 1

    elif button_clicked == 'archer':
        if self.resources.spend(wood=0, gold=30):
            v_x = self.village_pos_x // PIXEL_SIZE + 15
            v_y = self.village_pos_y // PIXEL_SIZE + 10
            from entity import Archer
            self.entities.players.add(Archer(v_x, v_y))
            self.resources.current_population += 1

    # (tower et wall seront implémentés jour 9)

    elif button_clicked is None:
        # Pas de bouton cliqué, c'est une sélection d'unité
        world_x = (mouse_x + self.camera.x) // PIXEL_SIZE
        world_y = (mouse_y + self.camera.y) // PIXEL_SIZE

        unit = self.selection.get_unit_at_position(world_x, world_y, self.entities.players)

        if unit:
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_LSHIFT]:
                self.selection.clear()
            self.selection.add_unit(unit)
        else:
            self.selection.clear()
```

---

### Après-midi (2-4h) : Mini-map

#### 1. Méthode draw minimap
**Fichier : `main.py` - Ajouter méthode :**
```python
def draw_minimap(self):
    # Config minimap
    minimap_size = 150
    minimap_x = SCREEN_SIZE[0] - minimap_size - 10
    minimap_y = 50

    # Fond noir
    minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
    pygame.draw.rect(self.screen, (0, 0, 0), minimap_rect)
    pygame.draw.rect(self.screen, (100, 100, 100), minimap_rect, 2)

    # Ratio monde -> minimap
    scale_x = minimap_size / WORLD_WIDTH
    scale_y = minimap_size / WORLD_HEIGHT

    # Village (vert)
    v_x = self.village_pos_x // PIXEL_SIZE
    v_y = self.village_pos_y // PIXEL_SIZE
    v_w = self.assets["village_map"].get_width() // PIXEL_SIZE
    v_h = self.assets["village_map"].get_height() // PIXEL_SIZE

    village_rect = pygame.Rect(
        minimap_x + int(v_x * scale_x),
        minimap_y + int(v_y * scale_y),
        max(2, int(v_w * scale_x)),
        max(2, int(v_h * scale_y))
    )
    pygame.draw.rect(self.screen, (0, 200, 0), village_rect)

    # Players (bleu)
    for player in self.entities.players:
        px = minimap_x + int(player.x * scale_x)
        py = minimap_y + int(player.y * scale_y)
        pygame.draw.circle(self.screen, (0, 100, 255), (px, py), 2)

    # Gobelins (rouge)
    for goblin in self.entities.goblins:
        gx = minimap_x + int(goblin.x * scale_x)
        gy = minimap_y + int(goblin.y * scale_y)
        pygame.draw.circle(self.screen, (255, 0, 0), (gx, gy), 2)

    # Vue caméra (rectangle blanc)
    cam_w = SCREEN_SIZE[0] // PIXEL_SIZE
    cam_h = SCREEN_SIZE[1] // PIXEL_SIZE
    cam_x_world = self.camera.x // PIXEL_SIZE
    cam_y_world = self.camera.y // PIXEL_SIZE

    view_rect = pygame.Rect(
        minimap_x + int(cam_x_world * scale_x),
        minimap_y + int(cam_y_world * scale_y),
        int(cam_w * scale_x),
        int(cam_h * scale_y)
    )
    pygame.draw.rect(self.screen, (255, 255, 255), view_rect, 1)
```

#### 2. Appeler draw_minimap
**Fichier : `main.py` dans `draw()` après draw_resources :**
```python
self.draw_resources()
self.draw_minimap()  # NOUVEAU
self.ui_manager.draw(self.screen, self.resources)
```

**✅ FIN JOUR 8 : UI propre avec boutons + tooltips + minimap**

---

## JOUR 9 - Dimanche 1/03 - 5-7h - BÂTIMENTS

### Objectif : Tours et Murs défensifs

### Matin (3h) : Créer système de bâtiments

#### 1. Créer classes de bâtiments
**Créer fichier : `building.py`**
```python
import pygame
import time
from utils import PIXEL_SIZE

class Building:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 200
        self.current_hp = 200
        self.type = "building"

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def is_dead(self):
        return self.current_hp <= 0

    def draw(self, screen, camera_x, camera_y):
        pass  # Override dans sous-classes


class Tower(Building):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "tower"
        self.attack_damage = 20
        self.attack_range = 5
        self.attack_cooldown = 1.5
        self.last_attack_time = 0

    def get_enemy_in_range(self, enemies):
        """Trouve ennemi le plus proche à portée"""
        closest = None
        min_dist = self.attack_range + 1

        for enemy in enemies:
            dist = abs(enemy.x - self.x) + abs(enemy.y - self.y)
            if dist <= self.attack_range and dist < min_dist:
                closest = enemy
                min_dist = dist

        return closest

    def attack(self, target):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            target.take_damage(self.attack_damage)
            self.last_attack_time = current_time
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        # Rectangle marron (tour)
        pos_x = (self.x * PIXEL_SIZE) - camera_x
        pos_y = (self.y * PIXEL_SIZE) - camera_y

        pygame.draw.rect(screen, (139, 69, 19),
                        (pos_x, pos_y, PIXEL_SIZE, PIXEL_SIZE))
        pygame.draw.rect(screen, (100, 50, 0),
                        (pos_x, pos_y, PIXEL_SIZE, PIXEL_SIZE), 3)

        # Barre de vie
        self.draw_healthbar(screen, camera_x, camera_y)

    def draw_healthbar(self, screen, camera_x, camera_y):
        bar_width = PIXEL_SIZE
        bar_height = 5

        pos_x = (self.x * PIXEL_SIZE) - camera_x
        pos_y = (self.y * PIXEL_SIZE) - camera_y - 10

        pygame.draw.rect(screen, (255, 0, 0), (pos_x, pos_y, bar_width, bar_height))

        hp_percent = self.current_hp / self.max_hp
        green_width = int(bar_width * hp_percent)
        pygame.draw.rect(screen, (0, 255, 0), (pos_x, pos_y, green_width, bar_height))


class Wall(Building):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = "wall"
        self.max_hp = 300
        self.current_hp = 300

    def draw(self, screen, camera_x, camera_y):
        # Rectangle gris (mur)
        pos_x = (self.x * PIXEL_SIZE) - camera_x
        pos_y = (self.y * PIXEL_SIZE) - camera_y

        pygame.draw.rect(screen, (120, 120, 120),
                        (pos_x, pos_y, PIXEL_SIZE, PIXEL_SIZE))
        pygame.draw.rect(screen, (80, 80, 80),
                        (pos_x, pos_y, PIXEL_SIZE, PIXEL_SIZE), 3)

        # Barre de vie
        self.draw_healthbar(screen, camera_x, camera_y)

    def draw_healthbar(self, screen, camera_x, camera_y):
        bar_width = PIXEL_SIZE
        bar_height = 5

        pos_x = (self.x * PIXEL_SIZE) - camera_x
        pos_y = (self.y * PIXEL_SIZE) - camera_y - 10

        pygame.draw.rect(screen, (255, 0, 0), (pos_x, pos_y, bar_width, bar_height))

        hp_percent = self.current_hp / self.max_hp
        green_width = int(bar_width * hp_percent)
        pygame.draw.rect(screen, (0, 255, 0), (pos_x, pos_y, green_width, bar_height))
```

#### 2. Ajouter buildings à Game
**Fichier : `main.py` dans `__init__` après entities :**
```python
from building import Tower, Wall
self.buildings = set()
self.build_mode = None  # None, 'tower', ou 'wall'
self.build_preview_pos = None
```

---

### Après-midi (2-4h) : Mode construction

#### 1. Gérer clics boutons construction
**Fichier : `main.py` dans `event()` - Compléter gestion boutons UI :**
```python
# Dans le bloc button_clicked :
elif button_clicked == 'tower':
    if self.resources.can_afford(30, 50):
        self.build_mode = 'tower'
        print("Mode construction : Tour")

elif button_clicked == 'wall':
    if self.resources.can_afford(20, 0):
        self.build_mode = 'wall'
        print("Mode construction : Mur")
```

#### 2. Preview placement
**Fichier : `main.py` dans `update()` :**
```python
# Après ui_manager.update() :
if self.build_mode:
    mouse_pos = pygame.mouse.get_pos()
    world_x = (mouse_pos[0] + self.camera.x) // PIXEL_SIZE
    world_y = (mouse_pos[1] + self.camera.y) // PIXEL_SIZE
    self.build_preview_pos = (world_x, world_y)
```

#### 3. Placer bâtiment
**Fichier : `main.py` dans `event()` - Modifier MOUSEBUTTONDOWN bouton 1 :**
```python
if event.button == 1:  # Clic gauche
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Mode construction actif ?
    if self.build_mode:
        world_x = (mouse_x + self.camera.x) // PIXEL_SIZE
        world_y = (mouse_y + self.camera.y) // PIXEL_SIZE

        # Vérifier collision
        can_build = True

        # Pas sur village
        v_x = self.village_pos_x // PIXEL_SIZE
        v_y = self.village_pos_y // PIXEL_SIZE
        v_w = self.assets["village_map"].get_width() // PIXEL_SIZE
        v_h = self.assets["village_map"].get_height() // PIXEL_SIZE

        if (world_x >= v_x and world_x < v_x + v_w and
            world_y >= v_y and world_y < v_y + v_h):
            can_build = False

        # Pas sur autre building
        for building in self.buildings:
            if building.x == world_x and building.y == world_y:
                can_build = False
                break

        if can_build:
            if self.build_mode == 'tower':
                if self.resources.spend(wood=30, gold=50):
                    self.buildings.add(Tower(world_x, world_y))
                    self.build_mode = None

            elif self.build_mode == 'wall':
                if self.resources.spend(wood=20, gold=0):
                    self.buildings.add(Wall(world_x, world_y))
                    self.build_mode = None

        # Annuler avec Echap géré plus bas

    # Vérifier si clic sur UI (code existant)
    # ...
```

#### 4. Annuler construction avec Echap
**Fichier : `main.py` dans `event()` KEYDOWN :**
```python
elif event.key == pygame.K_ESCAPE:
    self.build_mode = None
    print("Construction annulée")
```

#### 5. Dessiner buildings + preview
**Fichier : `main.py` - Ajouter méthode :**
```python
def draw_buildings(self):
    for building in self.buildings:
        building.draw(self.screen, self.camera.x, self.camera.y)

    # Preview placement
    if self.build_mode and self.build_preview_pos:
        x, y = self.build_preview_pos
        pos_x = (x * PIXEL_SIZE) - self.camera.x
        pos_y = (y * PIXEL_SIZE) - self.camera.y

        # Couleur selon type
        if self.build_mode == 'tower':
            color = (139, 69, 19, 128)  # Marron transparent
        else:  # wall
            color = (120, 120, 120, 128)  # Gris transparent

        # Surface transparente
        preview_surf = pygame.Surface((PIXEL_SIZE, PIXEL_SIZE), pygame.SRCALPHA)
        preview_surf.fill(color)
        self.screen.blit(preview_surf, (pos_x, pos_y))
```

**Fichier : `main.py` dans `draw()` après draw_entities :**
```python
self.draw_entities()
self.draw_buildings()  # NOUVEAU
self.draw_screen_selection()
```

#### 6. Tours attaquent automatiquement
**Fichier : `main.py` dans `move()` après gobelins :**
```python
# Tours attaquent
import time
current_time = time.time()

for building in self.buildings:
    if isinstance(building, Tower):
        enemy = building.get_enemy_in_range(self.entities.goblins)
        if enemy:
            building.attack(enemy)

# Supprimer buildings détruits
self.buildings = set(b for b in self.buildings if not b.is_dead())
```

#### 7. Gobelins attaquent buildings
**Fichier : `main.py` dans `move()` - Modifier boucle gobelins :**
```python
for goblin in list(self.entities.goblins):
    # Chercher player OU building à portée
    target_player = goblin.get_enemy_in_range(self.entities.players)

    # Chercher building à portée
    target_building = None
    for building in self.buildings:
        dist = abs(building.x - goblin.x) + abs(building.y - goblin.y)
        if dist <= goblin.attack_range:
            target_building = building
            break

    # Prioriser player
    if target_player:
        goblin.attack(target_player, current_time)
    elif target_building:
        goblin.attack(target_building, current_time)
    else:
        # Bouger
        goblin.move(self.entities.players)

        # Check village
        # ... (code existant)
```

**✅ FIN JOUR 9 : Système de construction (Tours + Murs) fonctionnel**

**Tâche coéquipier Jour 8-9 :** Créer sprites 48×48px pour tour et mur (Aseprite/Piskel)

---

## JOUR 10 - Lundi 2/03 - 5-7h - VARIÉTÉ ENNEMIS

### Objectif : 3 types de gobelins différents

### Toute la journée (5-7h)

#### 1. Créer variantes gobelins
**Fichier : `entity.py` - Ajouter classes :**
```python
class GoblinTank(Goblin):
    """Gobelin lent mais très résistant"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_hp = 150
        self.current_hp = 150
        self.attack_damage = 12
        self.move_speed = 0.15  # Plus lent
        # Modifier la méthode move pour prendre en compte move_speed

class GoblinFast(Goblin):
    """Gobelin rapide mais fragile"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_hp = 40
        self.current_hp = 40
        self.attack_damage = 8
        self.move_speed = 0.5  # Très rapide

class GoblinArcher(Goblin):
    """Gobelin à distance"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_hp = 60
        self.current_hp = 60
        self.attack_damage = 10
        self.attack_range = 3  # Portée longue !
```

#### 2. Spawn mixte
**Fichier : `wave_manager.py` - Modifier spawn_enemies :**
```python
def spawn_enemies(self, num_enemies):
    """Crée les gobelins aux bords de la map"""
    from entity import Goblin, GoblinTank, GoblinFast, GoblinArcher
    import random

    goblins = set()

    for i in range(num_enemies):
        # Spawn aléatoire sur les bords
        side = random.choice(['top', 'bottom', 'left', 'right'])

        if side == 'top':
            x = random.randint(0, WORLD_WIDTH - 1)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, WORLD_WIDTH - 1)
            y = WORLD_HEIGHT - 1
        elif side == 'left':
            x = 0
            y = random.randint(0, WORLD_HEIGHT - 1)
        else:  # right
            x = WORLD_WIDTH - 1
            y = random.randint(0, WORLD_HEIGHT - 1)

        # NOUVEAU - Type aléatoire
        rand = random.random()
        if rand < 0.5:
            goblin = Goblin(x, y)  # 50% normal
        elif rand < 0.7:
            goblin = GoblinFast(x, y)  # 20% rapide
        elif rand < 0.85:
            goblin = GoblinTank(x, y)  # 15% tank
        else:
            goblin = GoblinArcher(x, y)  # 15% archer

        goblins.add(goblin)

    return goblins
```

#### 3. Différencier visuellement
**Fichier : `main.py` - Modifier draw_entities :**
```python
for goblin in self.entities.goblins:
    self.draw_image("goblin", goblin.x, goblin.y)

    # NOUVEAU - Indicateur type
    from entity import GoblinTank, GoblinFast, GoblinArcher

    pos_x = (goblin.x * PIXEL_SIZE) - self.camera.x
    pos_y = (goblin.y * PIXEL_SIZE) - self.camera.y

    if isinstance(goblin, GoblinTank):
        # Cercle bleu = tank
        pygame.draw.circle(self.screen, (0, 100, 255),
                          (pos_x + PIXEL_SIZE//2, pos_y + PIXEL_SIZE//2), 5)
    elif isinstance(goblin, GoblinFast):
        # Cercle jaune = rapide
        pygame.draw.circle(self.screen, (255, 255, 0),
                          (pos_x + PIXEL_SIZE//2, pos_y + PIXEL_SIZE//2), 5)
    elif isinstance(goblin, GoblinArcher):
        # Cercle violet = archer
        pygame.draw.circle(self.screen, (200, 0, 200),
                          (pos_x + PIXEL_SIZE//2, pos_y + PIXEL_SIZE//2), 5)

    self.draw_healthbar(goblin)
```

**Tâche coéquipier Jour 10 :** Créer 3 sprites de gobelins différents (couleurs/tailles variées)

**✅ FIN JOUR 10 : 4 types d'ennemis avec comportements différents**

---

## JOUR 11 - Mardi 3/03 - 5-7h - SONS & MUSIQUE

### Objectif : Immersion audio

### Matin (3h) : Effets sonores

#### 1. Télécharger assets audio
Sites recommandés :
- freesound.org
- opengameart.org
- zapsplat.com (gratuit avec attribution)

Sons nécessaires :
- `click.wav` - Clic UI
- `sword.wav` - Attaque mêlée
- `arrow.wav` - Tir flèche
- `hit.wav` - Dégâts reçus
- `build.wav` - Construction
- `coin.wav` - Gold gagné
- `victory.wav` - Victoire
- `defeat.wav` - Défaite

Créer dossier : `assets/sounds/`

#### 2. Créer SoundManager
**Créer fichier : `sound_manager.py`**
```python
import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()

        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7

        # Charger sons (avec try/except si fichier manquant)
        try:
            self.sounds['click'] = pygame.mixer.Sound('assets/sounds/click.wav')
            self.sounds['sword'] = pygame.mixer.Sound('assets/sounds/sword.wav')
            self.sounds['arrow'] = pygame.mixer.Sound('assets/sounds/arrow.wav')
            self.sounds['hit'] = pygame.mixer.Sound('assets/sounds/hit.wav')
            self.sounds['build'] = pygame.mixer.Sound('assets/sounds/build.wav')
            self.sounds['coin'] = pygame.mixer.Sound('assets/sounds/coin.wav')
            self.sounds['victory'] = pygame.mixer.Sound('assets/sounds/victory.wav')
            self.sounds['defeat'] = pygame.mixer.Sound('assets/sounds/defeat.wav')

            # Ajuster volumes
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)

        except:
            print("⚠️ Certains sons n'ont pas pu être chargés")

    def play(self, sound_name):
        """Jouer un effet sonore"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_music(self, music_file, loop=True):
        """Jouer musique de fond"""
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except:
            print(f"⚠️ Musique {music_file} non trouvée")

    def stop_music(self):
        pygame.mixer.music.stop()
```

#### 3. Intégrer sons
**Fichier : `main.py` dans `__init__` :**
```python
from sound_manager import SoundManager
self.sound_manager = SoundManager()
self.sound_manager.play_music('assets/music/gameplay.mp3')  # Si musique disponible
```

#### 4. Jouer sons aux actions
**Exemples d'intégration :**

**Clic UI :**
```python
# Dans event() quand bouton cliqué
if button_clicked:
    self.sound_manager.play('click')
```

**Construction :**
```python
# Quand building placé
self.buildings.add(Tower(world_x, world_y))
self.sound_manager.play('build')
```

**Attaque :**
```python
# Dans entity.py, méthode attack
def attack(self, target, current_time):
    if current_time - self.last_attack_time >= self.attack_cooldown:
        target.take_damage(self.attack_damage)
        self.last_attack_time = current_time
        # Note: Passer sound_manager en paramètre ou via singleton
        return True
    return False
```

*Note : Pour simplifier, on peut jouer les sons depuis main.py dans la boucle move()*

---

### Après-midi (2-4h) : Musique

#### 1. Télécharger musiques
3 morceaux nécessaires :
- `menu.mp3` - Calme, accueillant
- `gameplay.mp3` - Tension modérée, boucle
- `victory.mp3` - Épique, triomphant

Sites : incompetech.com (Kevin MacLeod), freemusicarchive.org

Créer dossier : `assets/music/`

#### 2. Changer musique selon état
**Fichier : `main.py` dans `update()` :**
```python
# Changer musique si game state change
if self.game_state == "WON" and not hasattr(self, 'victory_music_played'):
    self.sound_manager.stop_music()
    self.sound_manager.play('victory')
    self.victory_music_played = True

elif self.game_state == "LOST" and not hasattr(self, 'defeat_music_played'):
    self.sound_manager.stop_music()
    self.sound_manager.play('defeat')
    self.defeat_music_played = True
```

**Tâche coéquipier Jour 11 :** Chercher et télécharger tous les assets audio (sons + musiques)

**✅ FIN JOUR 11 : Audio complet (SFX + musique)**

---

## JOUR 12 - Mercredi 4/03 - 5-7h - EFFETS VISUELS (JUICE)

### Objectif : Polish visuel

### Matin (3h) : Système de particules

#### 1. Créer système particules
**Créer fichier : `particles.py`**
```python
import pygame
import random

class Particle:
    def __init__(self, x, y, color, lifetime=1.0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.age += dt
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravité

    def is_dead(self):
        return self.age >= self.lifetime

    def draw(self, screen, camera_x, camera_y):
        alpha = int(255 * (1 - self.age / self.lifetime))
        color_with_alpha = (*self.color[:3], alpha)

        pos_x = int(self.x - camera_x)
        pos_y = int(self.y - camera_y)

        pygame.draw.circle(screen, self.color, (pos_x, pos_y), self.size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count, color):
        """Émettre des particules"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)

        # Retirer mortes
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, screen, camera_x, camera_y):
        for particle in self.particles:
            particle.draw(screen, camera_x, camera_y)
```

#### 2. Intégrer particules
**Fichier : `main.py` dans `__init__` :**
```python
from particles import ParticleSystem
self.particles = ParticleSystem()
```

**Fichier : `main.py` dans `update()` :**
```python
# Après wave manager update
self.particles.update(dt)
```

**Fichier : `main.py` dans `draw()` après entities :**
```python
self.draw_entities()
self.particles.draw(self.screen, self.camera.x, self.camera.y)  # NOUVEAU
self.draw_buildings()
```

#### 3. Particules sur mort
**Fichier : `main.py` dans `move()` - Modifier suppression morts :**
```python
# Supprimer morts avec particules
dead_players = [p for p in self.entities.players if p.is_dead()]
for player in dead_players:
    # Particules sang
    px = player.x * PIXEL_SIZE + PIXEL_SIZE // 2
    py = player.y * PIXEL_SIZE + PIXEL_SIZE // 2
    self.particles.emit(px, py, 20, (200, 0, 0))  # Rouge
    self.sound_manager.play('hit')

self.entities.players = set(p for p in self.entities.players if not p.is_dead())

dead_goblins = [g for g in self.entities.goblins if g.is_dead()]
for goblin in dead_goblins:
    # Particules vertes
    gx = goblin.x * PIXEL_SIZE + PIXEL_SIZE // 2
    gy = goblin.y * PIXEL_SIZE + PIXEL_SIZE // 2
    self.particles.emit(gx, gy, 15, (0, 200, 0))  # Vert

    # Drop gold
    self.resources.add(gold=2)

self.entities.goblins = set(g for g in self.entities.goblins if not g.is_dead())
```

---

### Après-midi (2-4h) : Shake & Flash

#### 1. Screen shake
**Fichier : `main.py` - Ajouter variables dans `__init__` :**
```python
self.screen_shake = 0
```

**Ajouter méthode :**
```python
def apply_screen_shake(self, intensity):
    """Déclencher shake écran"""
    self.screen_shake = intensity

def get_shake_offset(self):
    """Calculer offset aléatoire pour shake"""
    if self.screen_shake > 0:
        import random
        offset_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
        offset_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
        self.screen_shake *= 0.9  # Diminuer progressivement

        if self.screen_shake < 0.5:
            self.screen_shake = 0

        return offset_x, offset_y
    return 0, 0
```

**Fichier : `main.py` dans `draw()` - Appliquer shake :**
```python
def draw(self):
    self.screen.fill((255, 255, 255))

    # Shake offset
    shake_x, shake_y = self.get_shake_offset()

    if self.game_state == "PLAYING":
        # Temporairement ajuster caméra pour shake
        original_cam_x = self.camera.x
        original_cam_y = self.camera.y

        self.camera.x += shake_x
        self.camera.y += shake_y

        self.draw_map()
        self.draw_entities()
        # ... reste du draw

        # Restaurer caméra
        self.camera.x = original_cam_x
        self.camera.y = original_cam_y
```

**Déclencher shake quand village touché :**
```python
# Dans move() quand goblin touche village
if goblin_touches_village:
    self.village_hp -= 10
    self.apply_screen_shake(10)
    self.sound_manager.play('hit')
```

#### 2. Flash dégâts
**Fichier : `entity.py` - Modifier take_damage :**
```python
def take_damage(self, damage):
    self.current_hp -= damage
    if self.current_hp < 0:
        self.current_hp = 0

    # Flash visuel
    self.damage_flash = 0.2  # Durée flash en secondes
```

**Ajouter dans Entity.__init__ :**
```python
self.damage_flash = 0
```

**Fichier : `main.py` - Update flash :**
```python
# Dans move() après updates
for entity in list(self.entities.players) + list(self.entities.goblins):
    if entity.damage_flash > 0:
        entity.damage_flash -= dt
```

**Fichier : `main.py` - Dessiner flash :**
```python
# Dans draw_entities(), après blit sprite
if hasattr(player, 'damage_flash') and player.damage_flash > 0:
    # Overlay blanc
    flash_surf = pygame.Surface((PIXEL_SIZE, PIXEL_SIZE))
    flash_surf.fill((255, 255, 255))
    flash_surf.set_alpha(int(255 * (player.damage_flash / 0.2)))
    self.screen.blit(flash_surf, (pos_screen_x, pos_screen_y))
```

**✅ FIN JOUR 12 : Effets visuels (particules, shake, flash)**

---

## JOUR 13 - Jeudi 5/03 - 5-7h - BALANCE & UPGRADES

### Objectif : Gameplay équilibré + système d'amélioration

### Matin (3h) : Système d'upgrades

#### 1. Créer upgrade manager
**Créer fichier : `upgrade_manager.py`**
```python
class UpgradeManager:
    def __init__(self):
        self.village_armor_level = 0  # Réduit dégâts subis
        self.attack_boost_level = 0   # +damage global
        self.gold_boost_level = 0     # +génération gold

        self.max_level = 3

    def can_upgrade_village_armor(self, resources):
        if self.village_armor_level >= self.max_level:
            return False
        cost = 100 + (self.village_armor_level * 50)
        return resources.gold >= cost

    def upgrade_village_armor(self, resources):
        if self.can_upgrade_village_armor(resources):
            cost = 100 + (self.village_armor_level * 50)
            if resources.spend(wood=0, gold=cost):
                self.village_armor_level += 1
                return True
        return False

    def can_upgrade_attack(self, resources):
        if self.attack_boost_level >= self.max_level:
            return False
        cost = 80 + (self.attack_boost_level * 40)
        return resources.gold >= cost

    def upgrade_attack(self, resources):
        if self.can_upgrade_attack(resources):
            cost = 80 + (self.attack_boost_level * 40)
            if resources.spend(wood=0, gold=cost):
                self.attack_boost_level += 1
                return True
        return False

    def can_upgrade_gold(self, resources):
        if self.gold_boost_level >= self.max_level:
            return False
        cost = 60 + (self.gold_boost_level * 30)
        return resources.gold >= cost

    def upgrade_gold(self, resources):
        if self.can_upgrade_gold(resources):
            cost = 60 + (self.gold_boost_level * 30)
            if resources.spend(wood=0, gold=cost):
                self.gold_boost_level += 1
                return True
        return False

    def get_damage_reduction(self):
        """Réduction dégâts en %"""
        return self.village_armor_level * 0.1  # 10% par niveau

    def get_attack_bonus(self):
        """Bonus attaque flat"""
        return self.attack_boost_level * 5

    def get_gold_multiplier(self):
        """Multiplicateur gold"""
        return 1.0 + (self.gold_boost_level * 0.5)  # +50% par niveau
```

#### 2. Intégrer upgrades
**Fichier : `main.py` dans `__init__` :**
```python
from upgrade_manager import UpgradeManager
self.upgrades = UpgradeManager()
```

#### 3. Appliquer bonus
**Génération gold (dans update) :**
```python
if self.gold_timer >= 2.0:
    gold_gain = int(1 * self.upgrades.get_gold_multiplier())
    self.resources.add(gold=gold_gain)
    self.gold_timer = 0
```

**Dégâts au village (dans move) :**
```python
if goblin_touches_village:
    base_damage = 10
    actual_damage = int(base_damage * (1 - self.upgrades.get_damage_reduction()))
    self.village_hp -= actual_damage
```

**Bonus attaque unités (dans entity.py attack) :**
*Note : Nécessite de passer upgrades en param ou stocker globalement*

---

### Après-midi (2-4h) : Balance final + Menu upgrades

#### 1. Ajouter boutons upgrades à UI
**Fichier : `ui_manager.py` - Ajouter boutons :**
```python
# Dans __init__ après boutons existants
upgrade_x = screen_width - 150
self.buttons['upgrade_armor'] = UIButton(upgrade_x, 100, 140, 40, "Village +10%", cost_gold=100)
self.buttons['upgrade_attack'] = UIButton(upgrade_x, 150, 140, 40, "Attack +5", cost_gold=80)
self.buttons['upgrade_gold'] = UIButton(upgrade_x, 200, 140, 40, "Gold +50%", cost_gold=60)
```

#### 2. Gérer clics upgrades
**Fichier : `main.py` dans event() button_clicked :**
```python
elif button_clicked == 'upgrade_armor':
    if self.upgrades.upgrade_village_armor(self.resources):
        self.sound_manager.play('coin')
        print(f"Village Armor niveau {self.upgrades.village_armor_level}")

elif button_clicked == 'upgrade_attack':
    if self.upgrades.upgrade_attack(self.resources):
        self.sound_manager.play('coin')
        print(f"Attack Boost niveau {self.upgrades.attack_boost_level}")

elif button_clicked == 'upgrade_gold':
    if self.upgrades.upgrade_gold(self.resources):
        self.sound_manager.play('coin')
        print(f"Gold Boost niveau {self.upgrades.gold_boost_level}")
```

#### 3. Playtesting + ajustements

**Jouer 10 parties et ajuster :**

Balance à tester :
- Vague 1 : 5 gobelins (facile)
- Vague 5 : 17 gobelins (moyen)
- Vague 10 : 32 gobelins (dur)

Ajustements possibles :
```python
# Dans wave_manager.py
num_enemies = 3 + (self.current_wave - 1) * 2  # Si trop dur

# Dans entity.py - Stats gobelins
Goblin: hp=60, damage=8  # Si trop fort
Tower: damage=25, range=6  # Si trop faible

# Dans resources.py
self.gold = 150  # Start avec plus
```

**✅ FIN JOUR 13 : Upgrades + Balance final**

---

## JOUR 14 - Vendredi 6/03 - 5-7h - TESTING FINAL

### Objectif : Corriger tous les bugs

### Toute la journée (5-7h)

#### 1. Testing systématique (3h)

**Checklist à tester :**

- [ ] Démarrage jeu sans crash
- [ ] Sélection d'unités (clic gauche + zone)
- [ ] Déplacement unités (clic droit)
- [ ] Combat (players vs gobelins)
- [ ] Recrutement (Q = Warrior, W = Archer)
- [ ] Construction (E = Tour, R = Mur)
- [ ] Système de vagues (10 vagues)
- [ ] Win condition (survivre 10 vagues)
- [ ] Lose condition (village HP = 0)
- [ ] Ressources (gold auto, dépenses)
- [ ] Upgrades (3 types)
- [ ] Sons (tous les SFX)
- [ ] Musique (gameplay, victory, defeat)
- [ ] Particules (mort unités)
- [ ] UI (boutons, minimap, tooltips)
- [ ] Caméra (mouvement souris, drag)

**Cas limites :**
- Spam clic rapide
- Construire 100 tours
- Sélectionner toutes les unités
- Vague 15+ (si on survit 10)
- Redimensionner fenêtre pendant jeu

#### 2. Corrections bugs (2-3h)

Créer fichier `BUGS.md` :
```markdown
# BUGS TROUVÉS

## Critique (empêche de jouer)
- [ ] Bug 1 : ...
- [ ] Bug 2 : ...

## Majeur (gêne gameplay)
- [ ] Bug 3 : ...

## Mineur (cosmétique)
- [ ] Bug 4 : ...

## Nice-to-fix (si temps)
- [ ] Bug 5 : ...
```

Prioriser fixes critiques et majeurs.

#### 3. Optimisation (1h)

Si FPS < 30 :

**Profiling :**
```python
# Dans main.py, afficher FPS
def draw_resources(self):
    # ... (code existant)

    # FPS counter
    fps = int(self.clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    self.screen.blit(fps_text, (SCREEN_SIZE[0] - 100, SCREEN_SIZE[1] - 30))
```

**Optimisations possibles :**
- Limiter particules max (200)
- Culling plus agressif pour entities hors écran
- Cache des surfaces pygame
- Réduire fréquence update IA (1x toutes les 2 frames)

#### 4. Commit final
```bash
git add .
git commit -m "Version finale - Jeu complet et testé"
git push
```

**✅ FIN SEMAINE 2 : JEU COMPLET, TESTÉ, POLISH ! 🎉**

---

# 📝 SEMAINE 3 : DOCUMENTATION & PRÉSENTATION (7-13 mars)

## JOUR 15 - Mercredi 10/03 - 1h - HOTFIXES

Corriger les 2-3 bugs les plus critiques trouvés en semaine 2 qui n'ont pas été fixés.

---

## JOURS 16-17 - Week-end 8-9/03 - 4h - DOCUMENTATION

### Samedi (2h) : Rapport technique

**Structure rapport PDF (10-15 pages) :**

```markdown
# TROPHENSI - Village Defense RTS
## Trophées NSI 2026

### 1. INTRODUCTION (1 page)
- Contexte du projet
- Objectifs du jeu
- Technologies utilisées (Python 3.13, Pygame CE 2.6)

### 2. ANALYSE DU BESOIN (1-2 pages)
- Public cible
- Cahier des charges
- Fonctionnalités attendues

### 3. CONCEPTION (3-4 pages)
- Architecture logicielle (diagramme de classes)
- Schéma des interactions (joueur → UI → game logic)
- Diagramme entités-relations (Entity, Building, Resources...)
- Algorithmes clés :
  - Pathfinding (déplacement unités)
  - IA ennemis (poursuite + attaque)
  - Génération procédurale monde
  - Système de vagues

### 4. RÉALISATION (3-4 pages)
- Structure du code (modules, fichiers)
- Captures d'écran annotées
- Extraits de code commentés (algorithmes intéressants)
- Difficultés rencontrées et solutions

### 5. TESTS & VALIDATION (1 page)
- Tests effectués
- Cas limites gérés
- Balance gameplay

### 6. CONCLUSION (1 page)
- Bilan du projet
- Points forts / faibles
- Améliorations futures possibles

### 7. ANNEXES
- Guide utilisateur (touches, règles)
- Bibliographie / ressources
```

**Outils :** Word, Google Docs, ou LaTeX (Overleaf)

---

### Dimanche (2h) : Code documentation + README

#### 1. Docstrings complètes
**Ajouter docstrings à toutes les classes/méthodes :**

```python
class WaveManager:
    """
    Gère le système de vagues d'ennemis.

    Attributes:
        current_wave (int): Numéro de la vague actuelle (0 = pas encore commencé)
        is_wave_active (bool): True si une vague est en cours
        time_until_next_wave (float): Temps en secondes avant prochaine vague
    """

    def spawn_enemies(self, num_enemies):
        """
        Crée des gobelins aux bords de la carte.

        Args:
            num_enemies (int): Nombre d'ennemis à créer

        Returns:
            set[Goblin]: Ensemble des gobelins créés
        """
```

#### 2. README.md complet
**Fichier : `README.md`**
```markdown
# 🎮 TROPHENSI - Village Defense RTS

![Screenshot](screenshots/gameplay.png)

## 📝 Description

Jeu de stratégie en temps réel où vous défendez votre village contre des vagues de gobelins.
Recrutez des unités, construisez des défenses, et survivez 10 vagues pour gagner !

**Projet réalisé pour les Trophées NSI 2026**

## 🎯 Fonctionnalités

- ✅ Système RTS (sélection, déplacement, combat)
- ✅ 2 types d'unités jouables (Warrior, Archer)
- ✅ 4 types d'ennemis (Goblin, Tank, Rapide, Archer)
- ✅ Constructions défensives (Tours, Murs)
- ✅ Système de vagues progressif (10 vagues)
- ✅ Génération procédurale du monde
- ✅ Upgrades et économie
- ✅ Effets visuels et sonores

## 🛠️ Installation

### Prérequis
- Python 3.13+
- pip

### Étapes
```bash
# Cloner le repo
git clone https://github.com/votre-username/trophensi.git
cd trophensi

# Installer dépendances
pip install -r requirements.txt

# Lancer le jeu
python main.py
```

## 🎮 Comment jouer

### Objectif
Survivre 10 vagues de gobelins en défendant votre village.

### Contrôles
- **Clic gauche** : Sélectionner une unité
- **Clic droit** : Ordonner déplacement / Drag pour sélection zone
- **Shift + Clic** : Ajouter à la sélection
- **Q** : Recruter Warrior (20 gold)
- **W** : Recruter Archer (30 gold)
- **E** : Mode construction Tour (50g + 30w)
- **R** : Mode construction Mur (20w)
- **Échap** : Annuler construction

### Ressources
- **Gold** : Généré automatiquement (1 toutes les 2s, améliorable)
- **Wood** : Obtenu en tuant des gobelins ou via fermes (futur)

## 📁 Structure du projet

```
trophensi/
├── main.py              # Point d'entrée + Game loop
├── entity.py            # Entités (Player, Gobelins...)
├── building.py          # Bâtiments (Tour, Mur)
├── camera.py            # Système de caméra
├── selection.py         # Gestion sélection unités
├── resources.py         # Manager ressources
├── wave_manager.py      # Système de vagues
├── ui_manager.py        # Interface utilisateur
├── sound_manager.py     # Audio
├── particles.py         # Effets visuels
├── upgrade_manager.py   # Système d'upgrades
├── direction.py         # Enum directions
├── utils.py             # Constantes
└── assets/
    ├── entity/          # Sprites unités
    ├── map/             # Tilesets
    ├── sounds/          # Effets sonores
    └── music/           # Musiques
```

## 👥 Équipe

- **Développeur principal** : [Votre nom]
- **Contributeur** : [Nom coéquipier]

## 📜 Licence

Projet éducatif - Trophées NSI 2026

## 🙏 Crédits

- Engine : Pygame Community Edition
- Assets : [Sources des assets]
- Sons : freesound.org, opengameart.org
- Musiques : [Sources musiques]
```

#### 3. requirements.txt
**Créer fichier : `requirements.txt`**
```
pygame-ce>=2.6.1
```

---

## JOURS 18-19 - Lundi-Mardi 11-12/03 - 0h - BUFFER

Temps de sécurité pour finitions imprévues.

---

## JOUR 20 - Mercredi 13/03 - 1h - VIDÉO DÉMO

### Objectif : Vidéo 2-3 min

**Plan vidéo :**

1. **Intro (10s)**
   - Logo / Titre "TROPHENSI"
   - "Un RTS de défense par [Nom]"

2. **Présentation (20s)**
   - Vue du jeu
   - "Défendez votre village contre des vagues de gobelins"
   - Montrer map, village, ennemis

3. **Gameplay (90s)**
   - Sélection d'unités
   - Déplacement
   - Combat
   - Recrutement (Q/W)
   - Construction tour
   - Vague d'ennemis
   - Upgrades
   - Montrer minimap, UI

4. **Features techniques (30s)**
   - Génération procédurale
   - 4 types d'ennemis
   - Système de vagues
   - Particules

5. **Outro (10s)**
   - Écran victoire
   - "Merci !"
   - Contact / GitHub

**Outils :**
- **OBS Studio** (gratuit) pour capture écran
- **DaVinci Resolve** (gratuit) ou **Shotcut** pour montage
- **Audacity** pour voix off

**Tâche coéquipier :** Enregistrer voix off + montage vidéo

**Upload :** YouTube (non listée) ou Google Drive

---

# 📊 PRIORISATION SI RETARD

## ✅ MUST-HAVE (Ne PAS couper)
- Sélection + déplacement unités
- Combat fonctionnel
- Système de vagues (minimum 5 vagues pour gagner)
- Recrutement 2 types unités
- Win/Lose conditions
- UI basique ressources
- Documentation minimale (README + rapport 5 pages min)

## 🟡 SHOULD-HAVE (Garder si possible)
- Bâtiments (au moins tours)
- 3 types d'unités joueur
- 2 types ennemis
- UI propre avec boutons
- Sons basiques
- Mini-map
- Rapport complet

## 🔵 NICE-TO-HAVE (Couper si manque temps)
- Système d'upgrades
- 4 types d'ennemis
- Musique
- Effets visuels avancés (particules, shake)
- Variété bâtiments (murs, fermes)
- Vidéo démo professionnelle

---

# 💡 CONSEILS TROPHÉES NSI

## Ce que le jury regarde

### 1. Innovation (20%)
- Mécaniques originales
- Votre jeu : **Mix TD + RTS avec génération procédurale**
- Points forts à mettre en avant :
  - Système de vagues dynamique
  - IA ennemis avec comportements variés
  - Monde procédural

### 2. Technique (30%)
- Code propre et commenté
- Algorithmes intéressants
- Architecture logicielle
- **Mettre en avant :**
  - Pathfinding
  - Génération procédurale
  - Système d'événements
  - Pattern MVC (Model-View-Controller)

### 3. Réalisation (30%)
- Jeu fonctionnel sans bugs
- Polish visuel/sonore
- Tests effectués
- **Critères :**
  - Pas de crash pendant démo
  - Gameplay fluide
  - Win/Lose clairs

### 4. Présentation (20%)
- Rapport qualité
- Vidéo démo
- Soutenance orale
- **Tips :**
  - Rapport avec schémas/diagrammes
  - Vidéo < 3 min, dynamique
  - Préparer démo live (backup vidéo si crash)

---

## Pièges à éviter

### ❌ Code
- Code non commenté
- Variables en anglais mal nommées (x, tmp, data...)
- Pas de docstrings
- Fichier unique de 2000 lignes

### ❌ Gameplay
- Jeu impossible à gagner
- Trop facile (win en 30s)
- Bugs critiques (crash vague 5)
- Pas de feedback visuel

### ❌ Documentation
- Rapport < 8 pages
- Pas de schémas
- Copier-coller code sans explication
- Fautes d'orthographe

### ❌ Présentation
- Vidéo > 5 min (jury perd attention)
- Pas de son
- Qualité vidéo 240p
- Démo qui crash

---

# ✅ CHECKLIST FINALE (Avant rendu)

## Code
- [ ] Aucun bug critique (crashes)
- [ ] Code commenté (français OK)
- [ ] Docstrings sur classes/fonctions principales
- [ ] Variables bien nommées
- [ ] requirements.txt à jour
- [ ] README.md complet

## Jeu
- [ ] Menu principal ou lancement direct
- [ ] Partie complète jouable (début → victoire/défaite)
- [ ] Win condition claire (survivre 10 vagues)
- [ ] Lose condition claire (village détruit)
- [ ] FPS stable (> 30)
- [ ] Pas de crash pendant 10 min de jeu

## Documentation
- [ ] Rapport PDF (8-15 pages)
- [ ] Schémas / diagrammes (au moins 3)
- [ ] Captures d'écran annotées
- [ ] Extraits de code commentés
- [ ] Bibliographie / sources assets

## Médias
- [ ] Vidéo démo (2-3 min)
- [ ] Qualité vidéo HD (720p min)
- [ ] Voix off audible
- [ ] Upload YouTube/Drive accessible

## Rendu
- [ ] Dossier ZIP propre nommé "NOM_Prenom_TropheesNSI.zip"
- [ ] Contient : code source + rapport.pdf + lien_video.txt
- [ ] Testé sur autre PC (dépendances OK)
- [ ] Envoyé AVANT deadline (avec marge 1h)

---

# 📁 STRUCTURE FICHIERS FINALE

```
trophensi/
├── main.py
├── entity.py
├── building.py
├── camera.py
├── selection.py
├── resources.py
├── wave_manager.py
├── ui_manager.py
├── sound_manager.py
├── particles.py
├── upgrade_manager.py
├── direction.py
├── utils.py
├── README.md
├── requirements.txt
├── ROADMAP.md (ce fichier)
├── rapport.pdf
├── lien_video.txt
└── assets/
    ├── entity/
    │   ├── player/idle/1.png
    │   └── enemy/goblin/idle/1.png
    ├── map/
    │   ├── map_village.png
    │   └── tilesets/
    ├── sounds/
    │   ├── click.wav
    │   ├── sword.wav
    │   └── ...
    └── music/
        ├── gameplay.mp3
        └── victory.mp3
```

---

# 🎉 BON COURAGE !

**Cette roadmap est ton guide.** Suis-la jour par jour et tu auras un jeu impressionnant pour les Trophées NSI !

**Tips finaux :**
- 🔥 Committe sur Git CHAQUE SOIR
- 🧪 Teste SOUVENT (toutes les 2h)
- 📝 Note les bugs dans BUGS.md immédiatement
- ⏰ Respecte les deadlines de chaque jour
- 🤝 Délègue tâches non-critiques au coéquipier

**Questions ? Reviens vers moi pour des précisions sur n'importe quel jour !**

---

**Dernière mise à jour :** 19 février 2026
**Version :** 1.0
**Auteur roadmap :** Claude (Assistant IA)
