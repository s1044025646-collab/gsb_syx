import React, { useEffect, useState } from "react";
import AddNote from "../components/AddNote";
import NoteCard from "../components/NoteCard";
import Swal from "sweetalert2";
import { getAllNotes } from "../api/notes";

export default function Home() {
    const msgStyle = {
        justifyContent: "center",
        display: "flex",
        alignItems: "center",
        height: "50vh",
        color: "#aaa",
        letterSpacing: "1px",
        fontSize: "1.3em",
    };
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotes = async () => {
            try {
                const data = await getAllNotes();
                setNotes(data.content || []);
            } catch (err) {
                Swal.fire({
                    icon: "error",
                    title: "加载失败",
                    text: err.message || "获取笔记列表时出错",
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNotes();
    }, []);

    if (loading) {
        return (
            <div>
                <h1 className="headline">
                    Save Your <span>Notes</span> Here
                </h1>
                <p style={msgStyle}>加载中...</p>
            </div>
        );
    }

    return (
        <div>
            <h1 className="headline">
                Save Your <span>Notes</span> Here
            </h1>

            <div className="cards">
                {notes && notes.length > 0 ? (
                    notes.map((note) => (
                        <NoteCard key={note._id} note={note} />
                    ))
                ) : (
                    <p style={msgStyle}>No Notes To Show</p>
                )}
            </div>
            <AddNote />
        </div>
    );
}
