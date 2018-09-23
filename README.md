# Blockchain
First Cryptocurrency

This project is implemented to explore the basic concept of blockchain and cryptocurrency.I have created the 'needcoin' cryptocurrency using blockchain.
It is very basic implementation where I explore the concept of :
  1) Blockchain
	
  2)Transactions
	
  3)Consensus 
	
  4)Proof of work
	
  5)Decentralized the app

Project cointains 4 files that needs to be run as python program , it will run as a flask application on  port 5000,5001,5002,5003

1) User can call follwoing url to connect the nodes to the blockchain network

Request Url : http://127.0.0.1:5003/connect_node

Request Type : POST

Request Example: {
    "nodes": ["http://127.0.0.1:5000",
              "http://127.0.0.1:5001",
              "http://127.0.0.1:5002",
              "http://127.0.0.1:5003"]
              
}

2) User can get the existing blockchain on the node through the url:

node_port :[5000,5001,5002,5003]

Request Url : http://127.0.0.1:{{node_port}}/get_chain

Request Type : GET

3)User can apply the consensus on the node by hitting the following url:

  node_port :[5000,5001,5002,5003]
	
  Request Url : http://127.0.0.1:{{node}}/replace_chain
	
  Request Type : GET
  
 
4) User can add the transaction  by hitting the url on any node :
 
Request Url : http://127.0.0.1:{{node_port}}/add_transaction

Request Type : POST

Request Example: 
{
    "sender": "Mr A",
    "receiver": "Mr B",
    "amount": "10"
}


5) User can mine the block by hitting the url:

Request Url : http://127.0.0.1:{{node_port}}/mine_block

Request Type : POST

 
 


  
  
  
  
