import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from "react";
import Swal from "sweetalert2";
import { getNoteById, updateNote } from "../api/notes";

export default function EditForm() {
    const { id } = useParams();
    const [note, setNote] = useState({
        title: '',
        details: '',
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

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

    const changeHandler = (event) => {
        const {name, value} = event.target;
        setNote({ ...note, [name]: value });
    }

    const navigate = useNavigate();
    const submitHandler = async (event) => {
        event.preventDefault();
        setSaving(true);
        try {
            await updateNote(id, note);
            navigate(`/details/${id}`);
            Swal.fire('Your note has been updated successfully!')
        } catch (err) {
            Swal.fire({
                icon: "error",
                title: "更新失败",
                text: err.message || "更新笔记时出错",
            });
        } finally {
            setSaving(false);
        }
    }

    if (loading) {
        return (
            <div>
                <h1 className="headline">
                    Edit <span>Note</span>
                </h1>
                <p style={{ textAlign: 'center', marginTop: '50px', color: '#aaa' }}>加载中...</p>
            </div>
        );
    }

  return (
    <div>
            <h1 className="headline">
                Edit <span>Note</span>
            </h1>
            <form className="note-form" onSubmit={submitHandler}>
                <input
                    type="text"
                    name="title"
                    value={note.title}
                    onChange={changeHandler}
                    placeholder="Title of Note ..."
                />
                <textarea
                    name="details"
                    rows="5"
                    value={note.details}
                    onChange={changeHandler}
                    placeholder="Describe Your Note ..."
                ></textarea>
                <button type="submit" disabled={saving}>
                  {saving ? "保存中..." : "Save Changes"}
                </button>
            </form>
        </div>
  )
}
