from pengines.Builder import PengineBuilder
from pengines.Pengine import Pengine

pengine_builder = PengineBuilder(urlserver="http://localhost:4242")

pengine = Pengine(builder=pengine_builder)
pengine.create()

#query = "member(X, [1,2,3])"
#pengine.ask(query)
#print(pengine.currentQuery.availProofs)

#while pengine.currentQuery.hasMore:
#    pengine.doNext(pengine.currentQuery)
#    print(pengine.currentQuery.availProofs)

