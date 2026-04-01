import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import DetailCard from "../components/DetailCard";
import { getNoteById } from "../api/notes";
import Swal from "sweetalert2";

export default function NoteDetails() {
    const { id } = useParams();
    const [note, setNote] = useState({
        _id: "",
        title: "",
        details: "",
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNote = async () => {
            try {
                const data = await getNoteById(id);
                setNote(data.content);
            } catch (err) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: 'Failed to load note!',
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNote();
    }, [id]);

    if (loading) {
        return <div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>;
    }

    return (
        <div className="container">
            <DetailCard note={note} />
        </div>
    );
}
