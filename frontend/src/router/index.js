import { createRouter, createWebHistory } from "vue-router"

import Login from "../views/Login.vue"
import StudentRegister from "../views/StudentRegister.vue"
import CompanyRegister from "../views/CompanyRegister.vue"

import AdminDashboard from "../views/AdminDashboard.vue"
import StudentDashboard from "../views/StudentDashboard.vue"
import CompanyDashboard from "../views/CompanyDashboard.vue"

const routes = [

{
    path:"/",
    redirect:"/login"
},

{
    path:"/login",
    component:Login
},

{
    path:"/student-register",
    component:StudentRegister
},

{
    path:"/company-register",
    component:CompanyRegister
},

{
    path:"/admin",
    component:AdminDashboard,
    meta:{
        auth:true,
        role:"admin"
    }
},

{
    path:"/student",
    component:StudentDashboard,
    meta:{
        auth:true,
        role:"student"
    }
},

{
    path:"/company",
    component:CompanyDashboard,
    meta:{
        auth:true,
        role:"company"
    }
}

]

const router=createRouter({

history:createWebHistory(),

routes

})

router.beforeEach((to,from,next)=>{

const token=localStorage.getItem("token")
const role=localStorage.getItem("role")

if(to.meta.auth){
if(!token){
next("/login")
return
}

if(to.meta.role!=role){
next("/login")
return
}
}

next()
})

export default router