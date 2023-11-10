import React from 'react'
import axios from 'axios'
class Message extends React.Component
{
    state ={
        chat:[],
        msg:''
    }
    handleChange = (e)=>{
        console.log(e.target.value);
        this.setState({msg:e.target.value});
    }
    handleSend = ()=>{
        
        
        if(this.state.msg != '')
        {
            axios.post('http://127.0.0.1:5000/user',{'msg':this.state.msg})
            .then(res=>{
                let ch = this.state.chat;
                ch.push({from:'our',msag:this.state.msg});
                ch.push({from:'cb',msag:res.data});
                this.setState({chat:ch,msg:''});
                console.log(this.state);
                

            })
            .catch(err=>{
                console.log(err);
            });
            
            this.forceUpdate();
        }
        let interval = window.setInterval(function(){
            var elem = document.getElementById('chatt');
            elem.scrollTop = elem.scrollHeight;
            window.clearInterval(interval);
        },5000)
    }
    render()
    {
        return(
            <div  >
                <div id='chatt' style={{overflow:'scroll',overflowX:'hidden',height:'85vh'}}>
                    {
                        this.state.chat.map((msg)=>{
                            if(msg.from == 'cb')
                            {
                                return <div style={{flexWrap:'wrap',fontSize:'25px',fontFamily:'cursive',
                                marginBottom:'10px',borderRadius:'100px',marginRight:'500px',
                                padding:'30px',paddingBottom:'20px',width:'30%',
                                backgroundColor:'black',color:'white',float:'left',
                                display:'block'}}>{msg.msag} </div>
                            }
                            else{
                            return <div style={{flexWrap:'wrap',fontSize:'25px',fontFamily:'cursive',
                            marginBottom:'10px',borderRadius:'100px',marginLeft:'500px',
                            padding:'30px',paddingBottom:'20px',width:'30%',backgroundColor:'orange',
                            float:'right',display:'block',color:'whitesmoke'}}>{msg.msag}</div>
                            }
                        })
                    }
                </div>
                <div style={{height:'2vh'}}>
                    <input type='text' name='msg' 
                      onChange={(e)=>this.handleChange(e)} 
                      class="form-control"
                      
                      style={{marginLeft:'150px',width:'80%',float:'left'}}
                      value={this.state.msg} />
                      <button onClick={()=>this.handleSend()} style={{paddingLeft:'25px',paddingRight:'25px'}} class="btn btn-primary">Send</button>
                </div>
            </div>
        )
    }
}
export default Message;