import tkinter as tk
from tkinter import *
from tkinter import simpledialog
from typing import List, Tuple
import numpy as np
from numpy.random import randint


class Vertex:
    """ -----------------------------------------------------------------
    Classe qui modélise un sommet.
    ----------------------------------------------------------------- """

    def __init__(self, x, y, number=None):
        self.number = number
        self.x = x
        self.y = y


class Triangle:
    """ -----------------------------------------------------------------
    Classe qui modélise un triangle.
    ----------------------------------------------------------------- """

    def __init__(self, ID: int, vertices: List[Vertex], adjacents: List[int]):
        self.ID = ID
        self.vertices = vertices
        self.adjacents = adjacents
        self.center = None


class DelaunayTriangulationApp:
    """ -----------------------------------------------------------------
    Classe qui implémenter l'application pour la triangulation Delaunay.
    ----------------------------------------------------------------- """

    def __init__(self, height: int, width: int, displayNumbers=False):
        self.height = height
        self.width = width
        self.displayNumbers = displayNumbers

        self.next_vertex_id = 1
        self.next_triangle_id = 1

        self.TIN = {}
        self.lines = {}
        self.text_ids = []
        self.stack = []
        self.new_point = None
        self.universal = None
        self.delaunay = False

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        self.launch()

    def launch(self):
        """ -----------------------------------------------------------------
        Nom: launch
        Auteur: Corinne Dumais
        Description: Lance l'exécution de la fenêtre de l'application et formate le menu des options.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        # Paramètres de la fenêtre d'application
        self.root.title("Triangulation Delaunay")
        self.root.minsize(self.height, self.width)
        self.root.maxsize(self.height, self.width)

        # On crée le menu
        self.menubar = Menu(self.root)
        self.root.config(menu=self.menubar)

        self.app_menu = Menu(self.menubar, tearoff=False)
        self.triangulation_menu = Menu(self.menubar, tearoff=False)
        self.analysis_menu = Menu(self.menubar, tearoff=False)

        self.sub_draw = Menu(self.triangulation_menu, tearoff=False)
        self.sub_draw.add_command(label='Commencer', command=self.tracage_delaunay)
        self.sub_draw.add_command(label='Arrêter', command=self.stop_delaunay)
        self.sub_draw.entryconfigure(1, state='disabled')

        self.app_menu.add_command(label='Réinitialiser', command=self.clear)
        self.app_menu.add_command(label='Exit', command=self.root.destroy)

        self.triangulation_menu.add_cascade(label='Triangulation Delaunay', menu=self.sub_draw)
        self.triangulation_menu.add_command(label='Diagramme Voronoi', command=self.tracage_voronoi)
        self.triangulation_menu.entryconfigure(1, state='disabled')

        self.analysis_menu.add_command(label='Voisin le plus proche', command=self.voisin_plus_proche)
        self.analysis_menu.add_command(label='Voisins immédiats', command=self.voisins_immediats)
        self.analysis_menu.entryconfigure(0, state='disabled')
        self.analysis_menu.entryconfigure(1, state='disabled')

        self.menubar.add_cascade(label="Application", menu=self.app_menu)
        self.menubar.add_cascade(label="Triangulation", menu=self.triangulation_menu)
        self.menubar.add_cascade(label="Analyse spatiale", menu=self.analysis_menu)

        self.frame()
        self.root.mainloop()

    def clear(self):
        """ -----------------------------------------------------------------
        Nom: clear
        Auteur: Corinne Dumais
        Description: Réinitialise le triangle universel et l'exécution de l'application.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        # Réinitialisation des variables de triangulation
        self.next_vertex_id = 1
        self.next_triangle_id = 1
        self.TIN = {}
        self.lines = {}
        self.text_ids = []
        self.stack = []
        self.new_point = None
        self.delaunay = False
        self.universal = None

        # Réinitialisation du canvas
        self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        # Réinitialisation du menu des options
        self.analysis_menu.entryconfigure(0, state='disabled')
        self.analysis_menu.entryconfigure(1, state='disabled')
        self.triangulation_menu.entryconfigure(1, state='disabled')
        self.sub_draw.entryconfigure(0, state='normal')
        self.sub_draw.entryconfigure(1, state='disabled')

        self.launch()

    def frame(self):
        """ -----------------------------------------------------------------
        Nom: frame
        Auteur: Corinne Dumais
        Description: Formation du triangle universel.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        vertices = []

        # Affichage des sommets du triangle universel
        for x, y in [(randint(20, 80), randint(620, 680)), (randint(320, 380), randint(20, 80)),
                     (randint(620, 680), randint(620, 680))]:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')
            self.canvas.create_text(x + 7, y + 7, text=str(self.next_vertex_id), anchor="w", fill='red')
            vertices.append(Vertex(x, y, self.next_vertex_id))
            self.next_vertex_id += 1

        # On stocke le triangle universel
        self.TIN[self.next_triangle_id] = Triangle(self.next_triangle_id, vertices, [0, 0, 0])
        self.next_triangle_id += 1

        # On dessine le triangle universel
        vertex1, vertex2, vertex3 = vertices
        self.universal = self.canvas.create_polygon(vertex1.x, vertex1.y, vertex2.x, vertex2.y, vertex3.x, vertex3.y,
                                                    outline='black', fill='white')

    @staticmethod
    def determinant(p: Vertex, p1: Vertex, p2: Vertex) -> bool:
        """ -----------------------------------------------------------------
        Nom: determinant
        Auteur: Corinne Dumais
        Description: Calcule le déterminant pour déterminer si un point est à gauche d'un segment. Retourne faux si le
        déterminant est négatif, vrai sinon.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        determinant = np.linalg.det([[p1.x, p1.y, 1], [p2.x, p2.y, 1], [p.x, p.y, 1]])
        return determinant >= 0

    def walk(self, p: Vertex) -> int:
        """ -----------------------------------------------------------------
        Nom: walk
        Auteur: Corinne Dumais
        Description: Trouve le triangle qui contient le nouveau point. Retourne l'ID du triangle.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        # Commencer avec le triangle en position 1
        old_id = None
        next_id = 1
        found = False

        while not found:
            # Itérer sur chaque segment
            for i in range(3):
                success = self.determinant(p, self.TIN[next_id].vertices[i], self.TIN[next_id].vertices[(i + 1) % 3])
                if not success and self.TIN[next_id].adjacents[(i + 2) % 3] != 0 and self.TIN[next_id].adjacents[(i + 2) % 3] != old_id:
                    old_id = next_id
                    next_id = self.TIN[old_id].adjacents[(i + 2) % 3]
                    break
                if i == 2:
                    found = True

        return next_id

    def dessiner_nouveau_point(self):
        """ -----------------------------------------------------------------
        Nom: draw_new_point
        Auteur: Corinne Dumais
        Description: Attend le clic de l'utilisateur et dessine le nouveau point.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """

        def handle_click(event):
            if self.delaunay:
                if self.point_inside_universal(event.x, event.y, self.canvas.coords(self.universal)):
                    x, y = event.x, event.y
                    self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='red')
                    self.canvas.create_text(x + 7, y + 7, text=str(self.next_vertex_id), anchor="w", fill='red')
                    self.new_point = Vertex(x, y, self.next_vertex_id)
                    self.next_vertex_id += 1
                    self.canvas.unbind("<Button-1>")
                    self.canvas.quit()
                else:
                    print('Clicked outside universal triangle')
            else:
                self.canvas.unbind("<Button-1>")
                self.canvas.quit()

        self.canvas.bind("<Button-1>", handle_click)
        self.canvas.mainloop()

    def insert(self, p: Vertex, triangle_id: int):
        """ -----------------------------------------------------------------
        Nom: insert
        Auteur: Corinne Dumais
        Description: Insert le nouveau point dans le maillage.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        s1, s2, s3 = self.TIN[triangle_id].vertices
        a1, a2, a3 = self.TIN[triangle_id].adjacents

        # Configuration des nouveaux triangles
        new_id1 = self.next_triangle_id
        new_id2 = self.next_triangle_id + 1
        self.next_triangle_id += 2

        self.TIN[triangle_id] = Triangle(triangle_id, [p, s2, s3], [a1, new_id1, new_id2])
        self.TIN[new_id1] = Triangle(new_id1, [p, s3, s1], [a2, new_id2, triangle_id])
        self.TIN[new_id2] = Triangle(new_id2, [p, s1, s2], [a3, triangle_id, new_id1])

        # On met à jour les triangles adjacents
        for a in [a1, a2, a3]:
            if a != 0:
                for i in [triangle_id, new_id1, new_id2]:
                    if a in self.TIN[i].adjacents:
                        self.TIN[a].adjacents[self.TIN[a].adjacents.index(triangle_id)] = i

        # On ajoute les 3 nouveaux triangles à la pile
        self.stack.append(triangle_id)
        self.stack.append(new_id1)
        self.stack.append(new_id2)

        # On relie le nouveau point au sommet du triangle dans lequel il se trouve
        line_id1 = self.canvas.create_line(p.x, p.y, s1.x, s1.y)
        line_id2 = self.canvas.create_line(p.x, p.y, s2.x, s2.y)
        line_id3 = self.canvas.create_line(p.x, p.y, s3.x, s3.y)

        # On stocke les identificateurs des lignes pour pouvoir les effacer si nécessaire
        self.lines[tuple(sorted([(p.x, p.y), (s1.x, s1.y)], key=lambda x: x[0]))] = line_id1
        self.lines[tuple(sorted([(p.x, p.y), (s2.x, s2.y)], key=lambda x: x[0]))] = line_id2
        self.lines[tuple(sorted([(p.x, p.y), (s3.x, s3.y)], key=lambda x: x[0]))] = line_id3

    def optim(self):
        """ -----------------------------------------------------------------
        Nom: optim
        Auteur: Corinne Dumais
        Description: Optimise les triangles lorsque nécessaire jusqu'à ce que la pile soit vide
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        # On dépile tant qu'il y a des éléments dans la pile
        while self.stack:
            t1 = self.stack[-1]
            t2_idx = None
            for i, v in enumerate(self.TIN[t1].vertices):
                if v.number == self.new_point.number:
                    t2_idx = i

            self.stack.pop()
            t2 = self.TIN[t1].adjacents[t2_idx]

            # Il n'y a pas de triangle de ce côté là (extérieur du triangle universel)
            if t2 == 0:
                continue

            pc = []
            for i, v in enumerate(self.TIN[t1].vertices):
                if v in self.TIN[t2].vertices:
                    pc.append((i, v))

            t1_idx = self.TIN[t2].adjacents.index(t1)
            opposed_vertex = self.TIN[t2].vertices[t1_idx]

            # On vérifie si le triangle doit être optimisé
            if self.in_circle(self.TIN[t1], opposed_vertex):
                # Si oui, on inverse les diagonales
                pn, pnc, pc1, pc2 = self.swap(t1, t2)
                self.canvas.delete(self.lines[tuple(sorted([(pc1.x, pc1.y), (pc2.x, pc2.y)], key=lambda x: x[0]))])
                line_id = self.canvas.create_line(pn.x, pn.y, pnc.x, pnc.y, fill='black')
                self.lines[tuple(sorted([(pn.x, pn.y), (pnc.x, pnc.y)], key=lambda x: x[0]))] = line_id

    def swap(self, t1: int, t2: int) -> Tuple[Vertex, Vertex, Vertex, Vertex]:
        """ -----------------------------------------------------------------
        Nom: swap
        Auteur: Corinne Dumais
        Description: Échange les diagonales de deux triangles dont les ID sont t1 et t2.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        pc = []
        pn, pnc = None, None
        idx_pn = None
        for i, v in enumerate(self.TIN[t1].vertices):
            if v.number == self.new_point.number:
                pn = v
                idx_pn = i
            else:
                pc.append((i, v))

        assert len(pc) == 2, f"Two adjacent triangles should have exactly two vertices in common"

        if idx_pn == 1:
            pc1, pc2 = pc[1][1], pc[0][1]
            pc1_idx, pc2_idx = pc[1][0], pc[0][0]
        else:
            pc1, pc2 = pc[0][1], pc[1][1]
            pc1_idx, pc2_idx = pc[0][0], pc[1][0]

        t3 = self.TIN[t1].adjacents[pc1_idx]
        t4 = self.TIN[t1].adjacents[pc2_idx]

        pc1_idx, pc2_idx = None, None
        for i, v in enumerate(self.TIN[t2].vertices):
            if v.number in [n.number for n in self.TIN[t1].vertices]:
                if v.number == pc1.number:
                    pc1_idx = i
                elif v.number == pc2.number:
                    pc2_idx = i
                else:
                    print('Vertex number does not correspond to one of the two common points')
            else:
                pnc = v

        t5 = self.TIN[t2].adjacents[pc2_idx]
        t6 = self.TIN[t2].adjacents[pc1_idx]

        # On écrase les définitions de T1 et T2 avec leur nouvelle configuration
        self.TIN[t1] = Triangle(t1, [pn, pnc, pc2], [t6, t3, t2])
        self.TIN[t2] = Triangle(t2, [pn, pc1, pnc], [t5, t1, t4])

        # On met à jour les triangles adjacents de T4 et T6
        if t4 != 0:
            self.TIN[t4].adjacents[self.TIN[t4].adjacents.index(t1)] = t2
        if t6 != 0:
            self.TIN[t6].adjacents[self.TIN[t6].adjacents.index(t2)] = t1

        # On remet les triangles dans la pile pour retester
        self.stack.append(t1)
        self.stack.append(t2)

        return pn, pnc, pc[0][1], pc[1][1]

    @staticmethod
    def in_circle(triangle: Triangle, point: Vertex) -> bool:
        """ -----------------------------------------------------------------
        Nom: in_circle
        Auteur: Corinne Dumais
        Description: Détermine si un point est dans le cercle englobant un triangle.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        x, y = point.x, point.y
        x1, y1 = triangle.vertices[0].x, triangle.vertices[0].y
        x2, y2 = triangle.vertices[1].x, triangle.vertices[1].y
        x3, y3 = triangle.vertices[2].x, triangle.vertices[2].y

        z = x ** 2 + y ** 2
        z1 = x1 ** 2 + y1 ** 2
        z2 = x2 ** 2 + y2 ** 2
        z3 = x3 ** 2 + y3 ** 2

        H = np.linalg.det([[x, y, z, 1],
                           [x1, y1, z1, 1],
                           [x2, y2, z2, 1],
                           [x3, y3, z3, 1]])
        return H < 0

    @staticmethod
    def circumcircle(triangle: Triangle) -> Tuple[float, float]:
        """ -----------------------------------------------------------------
        Nom: circumcircle
        Auteur: Corinne Dumais
        Description: Calcule le centre circonscrit d'un triangle pour obtenir les vertex de Voronoi.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        x1, y1 = triangle.vertices[0].x, triangle.vertices[0].y
        x2, y2 = triangle.vertices[1].x, triangle.vertices[1].y
        x3, y3 = triangle.vertices[2].x, triangle.vertices[2].y

        z1 = x1 ** 2 + y1 ** 2
        z2 = x2 ** 2 + y2 ** 2
        z3 = x3 ** 2 + y3 ** 2

        P = np.linalg.det([[y1, z1, 1], [y2, z2, 1], [y3, z3, 1]])
        Q = -np.linalg.det([[x1, z1, 1], [x2, z2, 1], [x3, z3, 1]])
        R = np.linalg.det([[x1, y1, 1], [x2, y2, 1], [x3, y3, 1]])

        epsilon = 1E-4  # pour garantir la stabilité numérique
        xc = -0.5 * P / (R + epsilon)
        yc = -0.5 * Q / (R + epsilon)

        return xc, yc

    @staticmethod
    def point_inside_universal(x: float, y: float, vertices: List[float]) -> bool:
        """ -----------------------------------------------------------------
        Nom: point_inside_universal
        Auteur: Corinne Dumais
        Description: Détermine si un point est dans le triangle universel.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        x1, y1, x2, y2, x3, y3 = vertices
        # Calculate the area of the triangle and the areas of the sub-triangles formed by the point and each side of the triangle
        area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        area1 = abs((x1 - x) * (y2 - y) - (x2 - x) * (y1 - y))
        area2 = abs((x2 - x) * (y3 - y) - (x3 - x) * (y2 - y))
        area3 = abs((x3 - x) * (y1 - y) - (x1 - x) * (y3 - y))
        # The point is inside the triangle if the sum of the sub-triangle areas is equal to the area of the triangle
        return area == area1 + area2 + area3

    def tracage_delaunay(self):
        """ -----------------------------------------------------------------
        Nom: tracage_delaunay
        Auteur: Corinne Dumais
        Description: Prend des points fournis par l'utilisateur et fournit la triangulation Delaunay.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        self.delaunay = True
        self.sub_draw.entryconfigure(0, state='disabled')
        self.sub_draw.entryconfigure(1, state='normal')

        while self.delaunay:
            self.dessiner_nouveau_point()

            # On revérifie la condition car la valeur peut changer pendant qu'on attend un nouveau point dans draw_point
            if self.delaunay:
                id_triangle = self.walk(self.new_point)

                self.insert(self.new_point, id_triangle)

                self.optim()

        # Pour afficher les numéros des triangles dans chacun des triangles
        # Utile surtout pour débuggage
        # if self.displayNumbers:
        #     for tid in self.text_ids:
        #         self.canvas.delete(tid)
        #
        #     for i, t in self.TIN.items():
        #         cx = (t.vertices[0].x + t.vertices[1].x + t.vertices[2].x) / 3
        #         cy = (t.vertices[0].y + t.vertices[1].y + t.vertices[2].y) / 3
        #
        #         text_id = self.canvas.create_text(cx, cy, text=str(i), fill='blue')
        #         self.text_ids.append(text_id)

    def stop_delaunay(self):
        """ -----------------------------------------------------------------
        Nom: stop_delaunay
        Auteur: Corinne Dumais
        Description: Met fin à la triangulation Delaunay (après cet appel, l'utilisateur ne peut plus ajouter de point)
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        self.delaunay = False
        self.sub_draw.entryconfigure(1, state='disabled')
        self.triangulation_menu.entryconfigure(1, state='normal')
        self.analysis_menu.entryconfigure(0, state='normal')
        self.analysis_menu.entryconfigure(1, state='normal')

    def tracage_voronoi(self):
        """ -----------------------------------------------------------------
        Nom: tracage_voronoi
        Auteur: Corinne Dumais
        Description: Trace le diagramme de Voronoi correspondant à la triangulation Delaunay.
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        for tid, triangle in self.TIN.items():
            center = self.circumcircle(triangle)
            self.TIN[tid].center = center

        for tid, triangle in self.TIN.items():
            xc, yc = triangle.center
            for a in triangle.adjacents:
                if a != 0:
                    c = self.TIN[a].center
                    self.canvas.create_line(xc, yc, c[0], c[1], fill='red')

    def voisin_plus_proche(self):
        """ -----------------------------------------------------------------
        Nom: voisin_plus_proche
        Auteur: Corinne Dumais
        Description: Trouve et encercle le voisin le plus proche d'un point déterminé par l'utilisateur
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        def handle_click(event):
            if self.point_inside_universal(event.x, event.y, self.canvas.coords(self.universal)):
                x, y = event.x, event.y
                point = Vertex(x, y)
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='green')
                self.canvas.unbind("<Button-1>")
                self.canvas.quit()

                tid = self.walk(point)
                dist = []
                for i, v in enumerate(self.TIN[tid].vertices):
                    d = np.sqrt((point.x - v.x) ** 2 + (point.y - v.y) ** 2)
                    dist.append((i, d))
                sorted_dist = sorted(dist, key=lambda k: k[1])
                v = self.TIN[tid].vertices[sorted_dist[0][0]]
                self.canvas.create_oval(v.x - 6, v.y - 6, v.x + 6, v.y + 6, outline='green', width=2)
            else:
                print('Clicked outside universal triangle')

        self.canvas.bind("<Button-1>", handle_click)
        self.canvas.mainloop()

    def voisins_immediats(self):
        """ -----------------------------------------------------------------
        Nom: voisins_immediats
        Auteur: Corinne Dumais
        Description: Trouve et encercle tous les voisins immédiats d'un point identifié par l'utilisateur
        Date: 2023-13-03
        Version: 1.00
        ----------------------------------------------------------------- """
        point = simpledialog.askinteger("Voisins immédiats",
                                        f"Numéro du point (Entre 1 et {self.next_vertex_id - 1}): ", parent=self.root,
                                        minvalue=1,
                                        maxvalue=self.next_vertex_id - 1)
        for tid, triangle in self.TIN.items():
            if point in [n.number for n in triangle.vertices]:
                for t in triangle.vertices:
                    if t.number != point:
                        self.canvas.create_oval(t.x - 6, t.y - 6, t.x + 6, t.y + 6, outline='blue', width=2)


if __name__ == '__main__':
    DelaunayTriangulationApp(height=700, width=700)
