# Dosya: src/main.py
import sys
import os

# Python'un diğer klasörleri (simulation, map) görmesi için src yolunu ekliyoruz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.simulation_manager import Game

if __name__ == "__main__":
    game = Game()
    game.run()