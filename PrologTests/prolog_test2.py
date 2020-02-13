from pengines.Builder import PengineBuilder
from pengines.Pengine import Pengine
from prologterms import TermGenerator, PrologRenderer, Program, Var

P = TermGenerator()
X = Var('X')
Y = Var('Y')
Z = Var('Z')
R = PrologRenderer()

p = Program(
    P.ancestor(X,Y) <= (P.parent(X,Z), P.ancestor(Z,Y)),
    P.ancestor(X,Y) <= P.parent(X,Y),
    P.parent('a','b'),
    P.parent('b','c'),
    P.parent('c','d')
)

q = P.ancestor(X,Y)

factory = PengineBuilder(urlserver="http://localhost:4242",
                         srctext=R.render(p),
                         ask=R.render(q))
pengine = Pengine(builder=factory, debug=True)
while pengine.currentQuery.hasMore:
    pengine.doNext(pengine.currentQuery)
for p in pengine.currentQuery.availProofs:
    print('{} <- {}'.format(p[X.name], p[Y.name]))