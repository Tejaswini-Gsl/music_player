import copy

def merge_join(r, s, join_attrs):
    
    result = []
    
    pr = 0 # index of first tuple in r
    ps = 0 # index of first tuple in s
    count = 0
    while ps < len(s) and pr < len(r):
        
        ts = s[ps] 
        ss = [ts]
        
        ps += 1
        
        while ps < len(s) and s[ps][join_attrs] == ts[join_attrs]:
            ss.append(s[ps])
            ps += 1
            
        tr = r[pr]
        
        while pr < len(r) and r[pr][join_attrs] < ts[join_attrs]:
            pr += 1
            
        while pr < len(r) and r[pr][join_attrs] == ts[join_attrs]:
            for t in ss:
                result.append(copy.deepcopy(t) + copy.deepcopy(r[pr]))
            pr += 1
      
        # if s[ps]== IndexError:
        #     # print("PS:NULL")
        #     print("PR:NULL")
        

        print("PR:", r[pr])
        # print("PS:", s[ps])
        print("SS:", ss)
        print("ts:", ts)
        print("tr leave blank:", tr)
        
        count = count +1
        print(count)
        print("*********Round**************************")
    
    print(count)
    return result
    
r = [(13,'H','A'), (13,'I', 'L'), (15,'A', 'O'), (16,'O', 'P'), (17,'T', 'R'), (17,'Y','G'), (19,'L','B') ,(20,'D','L')]
s = [(13, 15), (14,30), (17, 25), (17,10),(18,40),(19,70)] 
print(merge_join(r, s, 0))