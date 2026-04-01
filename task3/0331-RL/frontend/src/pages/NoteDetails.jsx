import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Swal from "sweetalert2";
import DetailCard from "../components/DetailCard";
import { getNoteById } from "../api/notes";

export default function NoteDetails() {
    const { id } = useParams();
    const [note, setNote] = useState({
        id: "",
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
                    icon: "error",
                    title: "加载失败",
                    text: err.message || "获取笔记详情时出错",
                });
            } finally {
                setLoading(false);
            }
        };
        fetchNote();
    }, [id]);

    if (loading) {
        return (
            <div className="container">
                <p style={{ textAlign: 'center', marginTop: '50px', color: '#aaa' }}>加载中...</p>
            </div>
        );
    }

    return (
        <div className="container">
            <DetailCard note={note} />
        </div>
    );
}
