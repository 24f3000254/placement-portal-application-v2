<template>

<div class="container mt-4">
    <h2>Applicants</h2>

    <button
    class="btn btn-success mb-3"
    @click="exportApplications">
    Export Applicants CSV
    </button>

    <table class="table table-bordered">
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Skills</th>
                <th>Skills</th>
                <th>Resume</th>
                <th>Status</th>
                <th>Placement</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>

            <tr
            v-for="student in students"
            :key="student.application_id">
                <td>{{ student.name }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.branch }}</td>
                <td>{{ student.cgpa }}</td>
                <td>{{ student.skills }}</td>
                <td>
                    <button
                    v-if="student.resume"
                    class="btn btn-info btn-sm"
                    @click="viewResume(student.resume)">
                    View Resume
                    </button>

                    <span v-else>No Resume</span></td>
                <td>{{ student.status }}</td>
<td>

    <div v-if="student.status == 'Selected'">
        <input
        type="number"
        class="form-control mb-2"
        placeholder="Salary Package"
        v-model="student.salary">

        <input
        type="date"
        class="form-control mb-2"
        v-model="student.joining_date">

        <button
        class="btn btn-primary btn-sm"
        @click="placeStudent(student)">Mark Placed</button>
    </div>

    <span
    v-if="student.status == 'Placed'" class="badge bg-success">Placed</span>

</td>

<td>
    <button
    v-if="student.status != 'Placed'"
    class="btn btn-success btn-sm me-1"
    @click="updateStatus(student.application_id,'Shortlisted')">Shortlist</button>

    <button
    v-if="student.status != 'Placed'"
    class="btn btn-danger btn-sm me-1"
    @click="updateStatus(student.application_id,'Rejected')">Reject</button>

    <button
    v-if="student.status != 'Placed'"
    class="btn btn-primary btn-sm me-1"
    @click="updateStatus(student.application_id,'Selected')">Select</button>

    <br><br>

    <input
    v-if="student.status != 'Placed'"
    type="date"
    class="form-control mb-2"
    v-model="student.interview_date">

    <button
    v-if="student.status != 'Placed'"
    class="btn btn-warning btn-sm"
    @click="scheduleInterview(student.application_id,student.interview_date)">
    Schedule Interview</button>

</td>
            </tr>
        </tbody>
    </table>

</div>
</template>

<script setup>

import axios from "axios"
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"

const route = useRoute()
const students = ref([])

function loadApplicants(){
    axios.get(
        "http://127.0.0.1:5000/company/jobs/"+route.params.id+"/applications",
            {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }})

    .then((res)=>{
        students.value = res.data
    })
}

function updateStatus(id,status){
    axios.put(
        "http://127.0.0.1:5000/company/application/"+id,
        {
            status:status},

        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }})

    .then(()=>{
        alert("Status Updated")
        loadApplicants()
    })
}

function scheduleInterview(id,date){
    axios.put(
        "http://127.0.0.1:5000/company/application/"+id+"/interview",

        {
            interview_date:date},

        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")}}
    )
    .then(()=>{
        alert("Interview Scheduled")
        loadApplicants()
    })
}


function viewResume(filename){
    axios.get(
        "http://127.0.0.1:5000/company/resume/"+filename,
        {
            responseType:"blob",
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )
    .then((res)=>{
        let url = window.URL.createObjectURL(
            new Blob([res.data], {type:"application/pdf"})
        )
        window.open(url, "_blank")
    })
    .catch((err)=>{

        alert("Unable to open resume")
    })
}

function placeStudent(student){
    if(student.salary == "" || student.joining_date == ""){
        alert("Enter salary and joining date")
        return
    }

    axios.post(

        "http://127.0.0.1:5000/company/application/"+student.application_id+"/place",
        {
            salary:student.salary,
            joining_date:student.joining_date
        },
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )
    .then(()=>{

        alert("Student Placed")

        loadApplicants()

    })

    .catch((err)=>{

        alert(err.response.data.message)

    })

}

function exportApplications(){
axios.post(
    "http://127.0.0.1:5000/company/export-applications",
    {},
    {
        headers:{
            Authorization:"Bearer "+localStorage.getItem("token")
        }
    }
)

.then(res=>{
    alert("CSV export started")
    checkExport(res.data.task_id)
})
.catch(err=>{
    if(err.response){
        alert(err.response.data.message)
    }
})

}


function checkExport(taskId){

    let timer = setInterval(()=>{
        axios.get(
            "http://127.0.0.1:5000/export-status/"+taskId,
            {
                headers:{
                    Authorization:"Bearer "+localStorage.getItem("token")
                }
            }
        )

        .then(res=>{
            if(res.data.status == "SUCCESS"){
                clearInterval(timer)
                alert("CSV export completed")
                axios.get(
                    "http://127.0.0.1:5000/export-download/"+taskId,
                    {
                        responseType:"blob",
                        headers:{
                            Authorization:"Bearer "+localStorage.getItem("token")
                        }
                    }
                )
                .then(file=>{
                    let url = window.URL.createObjectURL(
                        new Blob([file.data])
                    )
                    let link = document.createElement("a")
                    link.href = url
                    link.setAttribute(
                        "download",
                        "company_applications.csv"
                    )
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                })
            }
            if(res.data.status == "FAILURE"){
                clearInterval(timer)
                alert("CSV export failed")
            }
        })
    },2000)
}

onMounted(()=>{
    loadApplicants()
})

</script>