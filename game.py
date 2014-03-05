#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import random
#import pygame._view		# For py2exe/py2app


# 背景色
BackgroundColor = (0, 0, 0)
# 死亡细胞颜色
DeadColor = (80, 80, 80)
# 复活细胞颜色
LiveColor = (255, 165, 0)


# 细胞
class Cell:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.is_dead = True


# 空间
class Space:
	def init(self, w, h):
		self.width = w
		self.height = h
		
		self.step_count = 0
		self.live_count = 0
		
		self.cells = []
		self.dead_list = []
		self.live_list = []
		
		# 初始化
		for x in xrange(self.width):
			self.cells.append([])
			for y in xrange(self.height):
				self.cells[x].append(Cell(x, y))
		
		self.reset()
	
	def fini(self):
		pass
	
	def neighbor(self):
		# 计算邻居细胞
		for l in self.cells:
			for c in l:
				c.neighbor = []
				nb_rect = ((c.x - 1, c.x + 1), (c.y - 1, c.y + 1))
				
				for x in xrange(nb_rect[0][0], nb_rect[0][1] + 1):
					x = self.width - 1 if x < 0 else 0 if x >= self.width else x

					for y in xrange(nb_rect[1][0], nb_rect[1][1] + 1):
						y = self.height - 1 if y < 0 else 0 if y >= self.height else y
						
						if x != c.x or y != c.y:
							c.neighbor.append(self.cells[x][y])
	
	def reset(self):
		self.step_count = 0
		self.live_count = 0
		
		# 设置存活率为 20%
		for l in self.cells:
			for c in l:
				r = random.random()
				c.is_dead = True
				if r < 0.2:
					self.live_list.append(c)
	
	def step(self):
		self.step_count += 1
		
		for l in self.cells:
			for c  in l:
				num = 0

				# 计算邻居的存活率
				for nb in c.neighbor:
					if not nb.is_dead:
						num += 1
				
				if num < 2 or num > 3:
					# num < 2 因孤单而死
					# num > 3 因拥挤而死
					if not c.is_dead:
						# 如果没死的就等死吧，已经死了就无视
						self.dead_list.append(c)
				elif num == 3:
					# num = 3 环境适宜，细胞等着复活吧，已经活着的就无视了
					if c.is_dead:
						self.live_list.append(c)
	
	
	def update(self, elapse, surface, size):
		
		surface.lock()
		
		# 画死亡细胞
		while len(self.dead_list):
			c = self.dead_list.pop()
			
			x = c.x * size
			y = c.y * size
			
			self.live_count -= 1
			
			c.is_dead = True
			pygame.draw.rect(surface, DeadColor, (x, y, size, size))
		
		# 画复活细胞
		while len(self.live_list):
			c = self.live_list.pop()
			
			x = c.x * size
			y = c.y * size
			
			self.live_count += 1
			
			c.is_dead = False
			pygame.draw.rect(surface, LiveColor, (x, y, size, size))
			
		surface.unlock()
		
		# 计算下一步细胞的存活状态
		self.step()


class Game:
	game_exit = False
	cell_size = 2
	sf_main = None
	sf_text = None
	
	def init(self):
		pygame.init()
		pygame.font.init()
		self.font = pygame.font.SysFont('arial', 16);
		
		pygame.display.set_caption('Game Of Life  |  Press <R> to reset')
		self.screen = pygame.display.set_mode((800, 600), 0, 24)
		self.screen.fill(BackgroundColor)
		
		# 游戏画面
		self.sf_main = pygame.Surface((800, 500))
		# 文字显示
		self.sf_text = pygame.Surface((800, 100))
		
		self.clock = pygame.time.Clock()
		
		self.space = Space();
		self.space.init(800 / self.cell_size, 500 / self.cell_size)
		
		self.sf_text.blit(self.font.render('Game Of Life ({0})'.format(self.space.width * self.space.height), True, (255, 255, 255)), (10, 10))
		self.sf_main.fill(DeadColor)
	
	def fini(self):
		self.space.fini()
		pygame.font.quit()
		pygame.quit()
	
	def run(self):
		last_fps = 0.0
		
		# 计算一次所有细胞的邻居
		self.space.neighbor()
		
		while not self.game_exit:
			elapse = self.clock.tick(60)
			
			for event in pygame.event.get():
				# 游戏结束
				if event.type == QUIT:
					self.game_exit = True
				
				if event.type == KEYUP:
					# 游戏重置
					if event.key == K_r:
						self.space.reset()
						self.sf_main.fill(DeadColor)
			
			# 更新世界
			self.space.update(elapse, self.sf_main, self.cell_size)
			fps = self.clock.get_fps()
			if last_fps != fps:
				last_fps = fps
				self.sf_text.fill(BackgroundColor, (10, 40, 150, 20))
				self.sf_text.blit(self.font.render('FPS: {0}'.format(last_fps), True, (255, 255, 255)), (10, 40))
			
			self.sf_text.fill(BackgroundColor, (200, 10, 100, 20))
			self.sf_text.blit(self.font.render('Live: {0}'.format(self.space.live_count), True, (255, 255, 255)), (200, 10))
			
			self.sf_text.fill(BackgroundColor, (200, 40, 100, 20))
			self.sf_text.blit(self.font.render('Step: {0}'.format(self.space.step_count), True, (255, 255, 255)), (200, 40))
			
			# 刷新到屏幕
			self.screen.blit(self.sf_main, (0, 0))
			self.screen.blit(self.sf_text, (0, 500))
			pygame.display.update()


def main():
	game = Game()
	game.init()
	game.run()
	game.fini()

if __name__ == '__main__':
	main()

