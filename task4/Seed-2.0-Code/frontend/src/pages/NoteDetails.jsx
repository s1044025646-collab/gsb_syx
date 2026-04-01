import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import DetailCard from "../components/DetailCard";
import { notesAPI } from "../api/notesAPI";
import Swal from "sweetalert2";

export default function NoteDetails() {
    const { id } = useParams();
    const [note, setNote] = useState({
        _id: "",
        title: "",
        details: "",
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNote = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await notesAPI.getNoteById(id);
                if (data.content) {
                    setNote(data.content);
                }
            } catch (err) {
                setError(err.message || 'Failed to fetch note');
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: err.message || 'Failed to fetch note',
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNote();
    }, [id]);

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
        );
    }

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#f5400f' }}>Error: {error}</div>
        );
    }

    return (
        <div className="container">
            <DetailCard note={note} />
        </div>
    );
}
