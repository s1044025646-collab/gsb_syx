import React, { Suspense, lazy } from "react";
import Head from "./components/Head";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

const Home = lazy(() => import("./pages/Home"));
const AddForm = lazy(() => import("./pages/AddForm"));
const NoteDetails = lazy(() => import("./pages/NoteDetails"));
const EditForm = lazy(() => import("./pages/EditForm"));

function App() {
    return (
        <>
            <Router>
                <Head />
                <Suspense fallback={<div style={{ textAlign: 'center', marginTop: '2rem' }}>Loading...</div>}>
                    <Routes>
                        <Route path={"/"} element={<Home />} />
                        <Route path={"/add"} element={<AddForm />}/>
                        <Route path={"/details/:id"} element={<NoteDetails />} />
                        <Route path={"/edit/:id"} element={<EditForm />} />
                    </Routes>
                </Suspense>
            </Router>
        </>
    );
}

export default App;
