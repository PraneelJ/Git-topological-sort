import sys
import zlib
import os

def topo_order_commits(commit_graph):
    #using Kahn's algorithm
    el_sorted= []
    root_hashes = []

    #add all root hashes 
    for item in commit_graph:
        if (len(commit_graph[item].parents) == 0):
            root_hashes.append(item)
    
    root_hashes= sorted(root_hashes)

    
    for item in commit_graph:
        commit_graph[item].children = sorted(commit_graph[item].children)
        commit_graph[item].parents = sorted(commit_graph[item].parents)
        
    
    while root_hashes:
        node = root_hashes.pop()
        el_sorted.append(node)


        for item in commit_graph[node].children.copy():
            commit_graph[item].parents.remove(node)
            commit_graph[node].children.remove(item)
            if (len(commit_graph[item].parents) == 0):
                root_hashes.append(item)

    return el_sorted

def find_git_dir():
    x = True
    dir_path = os.getcwd()

    while x == True:
        curr_path = dir_path+"/"+ ".git"


        if os.path.isdir(curr_path):
            return curr_path

        if (dir_path == "/"):
            sys.stderr.write("Not inside a Git repository\n")
            exit(1)

        dir_path = os.path.dirname(dir_path)


def find_git_branches(p):
    g_path = p + "/refs/heads"
    branch_dict = {}
    

    for root,dirs,files in os.walk(g_path):
        for filename in files:
             b_hash = ''
             
             with open(os.path.join(root, filename), 'r') as b_file:
                b_hash = b_file.read()

             branch_path = os.path.join(root, filename)
             branch_name = branch_path.split(".git/refs/heads/",1)[1]
             b_hash = b_hash.strip('\n')
             branch_dict[b_hash] = branch_name
    
    return branch_dict


class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()  


def build_commit_graph():

    #path of the /objects folder
    obj_path = find_git_dir() + "/objects"
    #print(obj_path)

    hash_par = {}
    commit_graph = {}


    for root,dirs,files in os.walk(obj_path):
        for filename in files:
            #get the hash id of the commit 
            h_id= root[root.rindex('/')+1:] + filename

            file_path = os.path.join(root, filename)
            

            #open file ,decompress contents and decode 
            compressed_contents = open(file_path, 'rb').read()
            decompressed_contents = zlib.decompress(compressed_contents)
            decoded_contents = decompressed_contents.decode(encoding='UTF-8',errors='ignore')
            #print(decoded_contents)
            
            #string to store parent hash 
            parent_hash = ''

            #check if the decoded contents describe a commit 
            if 'commit' in decoded_contents:
                #create hash id for all. 
                hash_par[h_id] = list()
                hash_par[h_id].append(0)

                #create commit nodes for all commit hashes 
                commit_graph[h_id] = CommitNode(h_id)

                #split decoded content into lines 
                p_step1 = decoded_contents.split('\n')
                
                
                #for each line in the decoded contents check if the line contains the parent hash 
                for substr in p_step1:
                
                    if ('parent' in substr):
                        if 0 in hash_par[h_id]:
                            hash_par[h_id].remove(0)
                        
                        parent_hash = substr.split("parent ",1)[1]
                        
                        hash_par[h_id].append(parent_hash)
                        commit_graph[h_id].parents.add(parent_hash)
                        
                       

    for item in commit_graph:
        for parent in commit_graph[item].parents:
            commit_graph[parent].children.add(item)
    

    return commit_graph



def print_topo_ordered_commits_with_branch_names(commit_nodes, topo_ordered_commits, head_to_branches):
    
    jumped = False
    for i in range(len(topo_ordered_commits)):
        commit_hash = topo_ordered_commits[i]
        if jumped:
            jumped = False
            sticky_hash = ' '.join( sorted(commit_nodes[commit_hash].children))
            print(f'={sticky_hash}')
        branches = head_to_branches[commit_hash] if commit_hash in head_to_branches else []
        
        print(commit_hash + (' '+branches if branches else ''))
        if i+1 < len(topo_ordered_commits) and topo_ordered_commits[i+1] not in commit_nodes[commit_hash].parents:
            jumped = True
            sticky_hash = ' '.join( sorted(commit_nodes[commit_hash].parents))
            print(f'{sticky_hash}=\n')
    


def main():

    #call the first method and store path in variable
    git_path = find_git_dir()

    
    #call the find branch method 
    fin_b_dict = find_git_branches(git_path)


    commit_graph = build_commit_graph()

    commit_copy = {}
    
    for item in commit_graph:
        commit_copy[item] = CommitNode(item)
        commit_copy[item].children = commit_graph[item].children.copy()
        commit_copy[item].parents = commit_graph[item].parents.copy()
   

    
    order = topo_order_commits(commit_copy)
    
    order.reverse()

    print_topo_ordered_commits_with_branch_names(commit_graph, order, fin_b_dict)





if __name__ == "__main__":
    main()

