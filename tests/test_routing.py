import unittest

from evacsim.config import CellType
from evacsim.environment.grid import Grid
from evacsim.routing.astar import astar_search
from evacsim.routing.bfs import bfs_search
from evacsim.routing.dijkstra import dijkstra_search
from evacsim.routing.route_manager import RouteManager


class TestRouting(unittest.TestCase):
    def setUp(self) -> None:
        self.grid = Grid(10)
        self.grid.fill_floor()

    def test_astar_direct_path(self) -> None:
        path = astar_search(self.grid, (0, 0), (9, 9))
        self.assertIsInstance(path, list)
        self.assertTrue(len(path) > 0)

    def test_bfs_direct_path(self) -> None:
        path = bfs_search(self.grid, (0, 0), (9, 9))
        self.assertIsInstance(path, list)
        self.assertTrue(len(path) > 0)

    def test_dijkstra_direct_path(self) -> None:
        path = dijkstra_search(self.grid, (0, 0), (9, 9))
        self.assertIsInstance(path, list)
        self.assertTrue(len(path) > 0)

    def test_astar_with_obstacles(self) -> None:
        for x in range(5):
            self.grid.set_cell(x, 5, CellType.WALL)
        path = astar_search(self.grid, (0, 0), (9, 9))
        self.assertIsInstance(path, list)

    def test_route_manager(self) -> None:
        manager = RouteManager(self.grid, algorithm="astar")
        path = manager.find_path((0, 0), (5, 5))
        self.assertIsInstance(path, list)

    def test_route_manager_replan(self) -> None:
        manager = RouteManager(self.grid, algorithm="astar")
        manager.find_path((0, 0), (5, 5))
        new_path = manager.replan((0, 0), (9, 9))
        self.assertIsInstance(new_path, list)

    def test_route_manager_switch_algorithm(self) -> None:
        manager = RouteManager(self.grid, algorithm="astar")
        manager.set_algorithm("bfs")
        self.assertEqual(manager.algorithm, "bfs")


if __name__ == "__main__":
    unittest.main()
