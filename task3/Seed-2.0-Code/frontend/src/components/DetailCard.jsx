import React from "react";
import { Link, useNavigate } from "react-router-dom";
import Swal from "sweetalert2";
import { notesAPI } from "../api/notesAPI";

export default function DetailCard({ note }) {
    const btnStyle = {
        padding: "0.5em 1em",
        fontSize: "1.1em",
        letterSpacing: "1px",
        background: "linear-gradient(#c53913, #f5400f)",
        color: "#f4f0e4",
        border: "none",
        borderRadius: "10px",
        cursor: "pointer",
        textDecoration: "none",
    };
    const navigate = useNavigate();
    const deleteNote = async () => {
        const result = await Swal.fire({
            title: "Are you sure?",
            text: "You won't be able to revert this!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes, delete it!",
        });
        if (result.isConfirmed) {
            try {
                await notesAPI.deleteNote(note._id);
                navigate("/");
                Swal.fire(
                    "Deleted!",
                    "Your Note has been deleted.",
                    "success"
                );
            } catch (err) {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: err.message || "Failed to delete note",
                });
            }
        }
    };
    return (
        <div className="note-details">
            <h1 className="title">{note.title}</h1>
            <p className="details">{note.details}</p>
            <div className="action">
                <Link style={btnStyle} to={`/edit/${note._id}`}>
                    {" "}
                    Edit
                </Link>
                <button style={btnStyle} onClick={deleteNote}>
                    Delete
                </button>
            </div>
        </div>
    );
}
