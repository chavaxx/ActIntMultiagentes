from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder

from random import randint

WIDTH = 10
HEIGHT = 10

class Wall(Agent):
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
	def step(self):
		pass

class Box(Agent):
	height = 1
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
	def step(self):
		pass

class Shelf(Agent):
	STATE = 0
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
	def step(self):
		pass

class Robot(Agent):
	WITH_BOX = 0
	WITHOUT_BOX = 1
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
		self.condition = self.WITHOUT_BOX
	def step(self):
		self.model.totalSteps = self.model.totalSteps + 1
		if self.condition == self.WITHOUT_BOX:
			next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
			next_move = self.random.choice(next_moves)
			while(self.model.matrix[next_move[1]][next_move[0]] == 1):
				next_move = self.random.choice(next_moves)
			self.model.grid.move_agent(self, next_move)
			pickedBox = self.model.grid.get_cell_list_contents([next_move])[0]
			if isinstance(pickedBox, Box):
				self.model.grid.remove_agent(pickedBox)
				self.condition = self.WITH_BOX

		if self.condition == self.WITH_BOX:
			next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
			next_move = self.random.choice(next_moves)

			while(self.model.matrix[next_move[1]][next_move[0]] == 1):
				next_move = self.random.choice(next_moves)
			self.model.grid.move_agent(self, next_move)
			isShelf = self.model.grid.get_cell_list_contents([next_move])[0]

			if(self.model.matrix[next_move[1]][next_move[0]] == 2 and isinstance(isShelf,Shelf)):
				if(isShelf.STATE<5):
					newBox= Box(self.model,next_move)
					newBox.height=isShelf.STATE
					self.model.grid.place_agent(newBox, newBox.pos)
					self.condition=self.WITHOUT_BOX
					self.model.schedule.add(newBox)
					isShelf.STATE = isShelf.STATE + 1
					self.model.boxesInPosition = self.model.boxesInPosition + 1
			else:
				self.model.grid.move_agent(self, next_move)

class Amazon(Model):
	totalSteps = 0
	maxSteps = 500
	currentSteps = 0
	boxNumber = 20
	boxesInPosition = 0
	def __init__(self):
		super().__init__()
		self.schedule = RandomActivation(self)
		self.grid = MultiGrid(WIDTH, HEIGHT, torus=False)

		self.matrix = [
			[1,1,1,1,1,1,1,1,1,1],
			[1,0,0,0,0,1,0,0,0,1],
			[1,0,0,0,0,1,0,0,0,1],
			[1,0,0,0,0,0,0,0,0,1],
			[1,0,0,2,0,0,0,0,2,1],
			[1,0,0,2,0,0,0,0,2,1],
			[1,0,0,0,0,0,0,0,0,1],
			[1,0,0,0,0,1,0,0,0,1],
			[1,0,0,0,0,1,0,0,0,1],
			[1,1,1,1,1,1,1,1,1,1],
		]

		for _,x,y in self.grid.coord_iter():
			if self.matrix[y][x] == 1:
				wall = Wall(self, (x,y))
				self.grid.place_agent(wall, wall.pos)
			elif self.matrix[y][x] == 2:
				pallet = Shelf(self, (x,y))
				self.grid.place_agent(pallet, pallet.pos)

		for _ in range(5):
			x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			while self.matrix[y][x] == 1:
				x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			robot = Robot(self, (x,y))
			self.grid.place_agent(robot, robot.pos)
			self.schedule.add(robot)

		for _ in range(self.boxNumber):
			x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			while self.grid.is_cell_empty((x,y)) == False:
				x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			box = Box(self, (x,y))
			self.grid.place_agent(box, box.pos)
			self.schedule.add(box)

	
	def step(self):
		if self.currentSteps<=self.maxSteps and self.boxesInPosition<self.boxNumber:
			self.schedule.step()
			print("total de pasos realizados por todos los agentes: ")
			print(self.totalSteps)
			print("numero de cajas que faltan ordenar: ")
			print(self.boxNumber - self.boxesInPosition)
			print("pasos de simulacion restantes: ")
			print(self.maxSteps - self.currentSteps)
			self.currentSteps = self.currentSteps + 1
