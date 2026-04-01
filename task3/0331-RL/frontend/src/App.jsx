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
                <Suspense fallback={
                    <p style={{ textAlign: 'center', marginTop: '50px', color: '#aaa' }}>加载中...</p>
                }>
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
