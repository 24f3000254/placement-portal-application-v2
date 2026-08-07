<template>

<div class="container mt-4">

    <h2>Applicants</h2>

    <table class="table table-bordered">

        <thead>

            <tr>

                <th>Name</th>
                <th>Email</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Skills</th>
                <th>Status</th>
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

                <td>{{ student.status }}</td>

                <td>

                    <button
                    class="btn btn-success btn-sm me-1"
                    @click="updateStatus(student.application_id,'Shortlisted')">
                        Shortlist</button>

                    <button
                    class="btn btn-danger btn-sm me-1"
                    @click="updateStatus(student.application_id,'Rejected')">

                        Reject</button>

                    <button
                    class="btn btn-primary btn-sm me-1"
                    @click="updateStatus(student.application_id,'Selected')">

                        Select</button>

                    <br><br>

                    <input
                    type="date"
                    class="form-control mb-2"
                    v-model="student.interview_date">

                    <button
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
            status:status
        },

        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then(()=>{
        alert("Status Updated")
        loadApplicants()
    })
}

function scheduleInterview(id,date){
    axios.put(
        "http://127.0.0.1:5000/company/application/"+id+"/interview",

        {
            interview_date:date
        },

        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then(()=>{
        alert("Interview Scheduled")
        loadApplicants()
    })
}

onMounted(()=>{
    loadApplicants()
})

</script>