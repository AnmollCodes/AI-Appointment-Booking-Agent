import AdminDashboard from './AdminDashboard'

// Use VITE_API_URL if set (Production), otherwise localhost (Development)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// --- FUTURISTIC SPACE BACKGROUND ---
function Asteroid({ position, color, scale }) {
    const mesh = useRef()
    useFrame((state, delta) => {
        if (mesh.current) {
            mesh.current.rotation.x += delta * 0.5
            mesh.current.rotation.y += delta * 0.3
        }
    })
    return (
        <Float speed={2} rotationIntensity={1} floatIntensity={1}>
            <Octahedron ref={mesh} position={position} scale={scale} args={[1, 0]}>
                <MeshDistortMaterial color={color} roughness={0.4} metalness={0.8} distort={0.2} speed={2} />
            </Octahedron>
        </Float>
    )
}

function ShootingStar() {
    // Simulating a shooting star with a fast moving trail
    const ref = useRef()
    const [active, setActive] = useState(false)

    useFrame((state, delta) => {
        if (!active && Math.random() > 0.995) { // Random trigger
            setActive(true)
            if (ref.current) {
                ref.current.position.set(Math.random() * 20 - 10, Math.random() * 10 + 5, -10)
            }
        }
        if (active && ref.current) {
            ref.current.position.x += delta * 15
            ref.current.position.y -= delta * 15
            if (ref.current.position.y < -10) setActive(false)
        }
    })

    return (
        <mesh ref={ref} visible={active}>
            <sphereGeometry args={[0.05, 8, 8]} />
            <meshBasicMaterial color="#00f260" />
            <Trail width={2} length={8} color={new THREE.Color("#00f260")} attenuation={(t) => t * t}>
                <meshBasicMaterial color="#00f260" />
            </Trail>
        </mesh>
    )
}

function FuturisticSpace({ state }) {
    const groupRef = useRef()
    useFrame((state, delta) => {
        if (groupRef.current) {
            groupRef.current.rotation.y += delta * 0.05 // Constant rotation
        }
    })

    return (
        <group ref={groupRef}>
            <color attach="background" args={['#020205']} />

            {/* Deep Starfield */}
            <Stars radius={100} depth={50} count={8000} factor={6} saturation={1} fade speed={2} />

            {/* Nebula Clouds (Fake) */}
            <pointLight position={[10, 10, 10]} intensity={2} color="#00c6ff" />
            <pointLight position={[-10, -10, -10]} intensity={2} color="#f093fb" />
            <ambientLight intensity={0.2} />

            {/* Asteroids Field */}
            <Asteroid position={[4, 2, -5]} color="#555" scale={0.5} />
            <Asteroid position={[-5, -3, -8]} color="#333" scale={0.8} />
            <Asteroid position={[0, 4, -10]} color="#444" scale={0.3} />
            <Asteroid position={[6, -5, -6]} color="#222" scale={0.6} />

            {/* Space Dust */}
            <Sparkles count={500} scale={15} size={2} speed={1} opacity={0.6} color="#00f260" />
        </group>
    )
}

// Need THREE for Color
import * as THREE from 'three'

// --- VIBRANT COMPONENTS ---

const NeonMessage = ({ msg, onSlotClick }) => {
    const isBot = msg.role === 'agent'
    const isConfirmation = msg.type === 'confirmation_card'

    const variants = {
        hidden: { opacity: 0, x: isBot ? -50 : 50, scale: 0.8 },
        visible: { opacity: 1, x: 0, scale: 1, transition: { type: 'spring', bounce: 0.4 } }
    }

    if (isConfirmation) {
        return (
            <motion.div
                initial="hidden" animate="visible" variants={variants}
                style={{ width: '100%', display: 'flex', justifyContent: 'center', margin: '30px 0' }}
            >
                <div style={{
                    padding: '30px', borderRadius: '20px', maxWidth: '450px', width: '100%',
                    background: 'rgba(0,0,0,0.6)', border: '1px solid #00f260',
                    boxShadow: '0 0 30px rgba(0, 242, 96, 0.2)',
                    backdropFilter: 'blur(10px)', textAlign: 'center'
                }}>
                    <div style={{ margin: '0 auto 15px', width: '60px', height: '60px', borderRadius: '50%', border: '2px solid #00f260', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px #00f260' }}>
                        <CheckCircle2 color="#00f260" size={30} />
                    </div>
                    <h3 style={{ color: '#00f260', margin: 0, fontSize: '1.4rem', textTransform: 'uppercase', letterSpacing: '2px' }}>Mission Confirmed</h3>
                    <p style={{ color: '#e0e0e0', marginTop: '10px' }}>{msg.text}</p>
                </div>
            </motion.div>
        )
    }

    return (
        <motion.div
            initial="hidden" animate="visible" variants={variants}
            style={{
                alignSelf: isBot ? 'flex-start' : 'flex-end',
                maxWidth: '75%',
                marginBottom: '15px'
            }}
        >
            <div
                style={{
                    padding: '16px 22px',
                    borderRadius: isBot ? '20px 20px 20px 4px' : '20px 20px 4px 20px',
                    // COLORFUL BACKGROUNDS
                    background: isBot
                        ? 'rgba(20, 20, 30, 0.8)'
                        : 'linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)',
                    border: isBot ? '1px solid rgba(255,255,255,0.1)' : 'none',
                    borderLeft: isBot ? '4px solid #f093fb' : 'none', // Neon accent for bot
                    color: 'white',
                    boxShadow: isBot ? 'none' : '0 10px 20px -5px rgba(0, 114, 255, 0.4)',
                    fontSize: '1rem',
                    lineHeight: '1.5'
                }}
            >
                {msg.text}
            </div>

            {msg.type === 'slots' && (
                <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {msg.data.map((slot, i) => (
                        <motion.button
                            key={slot}
                            whileHover={{ scale: 1.1, backgroundColor: '#f093fb', color: 'black' }}
                            onClick={() => onSlotClick(slot)}
                            style={{
                                background: 'rgba(255,255,255,0.1)',
                                border: '1px solid #f093fb',
                                color: '#f093fb',
                                padding: '8px 14px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}
                        >
                            {new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </motion.button>
                    ))}
                </div>
            )}
        </motion.div>
    )
}

// --- MAIN ---
export default function App() {
    const [messages, setMessages] = useState([
        { role: 'agent', text: 'Systems Online. Welcome to the Universal Booking Interface.', type: 'text' }
    ])
    const [inputValue, setInputValue] = useState('')
    const [systemState, setSystemState] = useState('idle')
    const [showAdmin, setShowAdmin] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const messagesEndRef = useRef(null)

    useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, systemState])

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = useRef(SpeechRecognition ? new SpeechRecognition() : null);

    useEffect(() => {
        if (recognition.current) {
            recognition.current.onresult = (ev) => {
                const tr = ev.results[0][0].transcript;
                setInputValue(tr);
                handleSend(tr);
                setIsListening(false);
            };
            recognition.current.onend = () => setIsListening(false);
        }
    }, [])

    const toggleMic = () => {
        if (!recognition.current) return;
        if (isListening) { recognition.current.stop(); setIsListening(false); }
        else { recognition.current.start(); setIsListening(true); }
    }

    const speak = (text) => {
        if (!window.speechSynthesis) return;
        const u = new SpeechSynthesisUtterance(text);
        const v = window.speechSynthesis.getVoices().find(v => v.name.includes("Google US English") || v.name.includes("Female"));
        if (v) u.voice = v;
        window.speechSynthesis.speak(u);
    }

    const handleSend = async (text = null) => {
        const userMsg = text || inputValue.trim()
        if (!userMsg) return
        setMessages(prev => [...prev, { role: 'user', text: userMsg, type: 'text' }])
        setInputValue('')
        setSystemState('thinking')

        try {
            const history = messages.map(m => ({ role: m.role === 'agent' ? 'assistant' : 'user', content: m.text }))
            const res = await axios.post(`${API_URL}/chat`, { session_id: 'space-user', message: userMsg, history })
            const { text: responseText, data } = res.data

            setTimeout(() => {
                let msgType = 'text'; let msgData = null
                if (data?.type === 'slots') {
                    msgType = 'slots'; msgData = (data.slots && data.slots[0] && typeof data.slots[0] === 'object') ? data.slots.map(s => s.start) : data.slots
                } else if (data?.type === 'confirmation') {
                    msgType = 'confirmation_card'; setSystemState('success'); setTimeout(() => setSystemState('idle'), 3000)
                } else { setSystemState('idle') }
                setMessages(prev => [...prev, { role: 'agent', text: responseText, type: msgType, data: msgData }])
                speak(responseText)
            }, 800)
        } catch (error) {
            setSystemState('idle')
            setMessages(prev => [...prev, { role: 'agent', text: "Signal Lost. Please retry.", type: 'text' }])
        }
    }
    const handleSlotClick = (slot) => handleSend(`Book ${new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`)

    return (
        <div style={{ width: '100vw', height: '100vh', position: 'relative', background: '#020205', fontFamily: "'Segoe UI', Roboto, sans-serif", color: 'white' }}>
            {/* Background */}
            <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
                <Canvas camera={{ position: [0, 0, 5], fov: 60 }}>
                    <FuturisticSpace state={systemState} />
                </Canvas>
            </div>

            {/* UI Layer */}
            <div style={{ position: 'absolute', inset: 0, zIndex: 10, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
                <div style={{
                    width: '100%', maxWidth: '850px', height: '90vh',
                    background: 'rgba(10, 10, 20, 0.4)', backdropFilter: 'blur(8px)',
                    borderRadius: '24px', border: '1px solid rgba(255,255,255,0.1)',
                    display: 'flex', flexDirection: 'column', overflow: 'hidden',
                    boxShadow: '0 0 50px rgba(0, 198, 255, 0.1)'
                }}>
                    {/* Header */}
                    <div style={{ padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <Rocket color="#00c6ff" />
                            <h1 style={{ margin: 0, fontSize: '1.2rem', background: 'linear-gradient(to right, #00c6ff, #0072ff)', WebkitBackgroundClip: 'text', color: 'transparent', fontWeight: 900 }}>UNIVERSAL AGENT</h1>
                        </div>
                        <button onClick={() => setShowAdmin(!showAdmin)} style={{ background: 'transparent', border: 'none', color: '#555', cursor: 'pointer' }}><Lock size={16} /></button>
                    </div>

                    {/* Messages */}
                    <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
                        <AnimatePresence>
                            {messages.map((m, i) => <NeonMessage key={i} msg={m} onSlotClick={handleSlotClick} />)}
                        </AnimatePresence>
                        {systemState === 'thinking' && (
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ color: '#f093fb', fontSize: '0.9rem', padding: '10px', fontStyle: 'italic' }}>
                                Computing trajectory...
                            </motion.div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div style={{ padding: '20px', background: 'rgba(0,0,0,0.3)', display: 'flex', gap: '15px' }}>
                        <input
                            value={inputValue} onChange={e => setInputValue(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleSend()}
                            placeholder="Type command..."
                            style={{ flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '15px', color: 'white', outline: 'none' }}
                        />
                        <button onClick={toggleMic} style={{ width: '50px', borderRadius: '12px', border: 'none', background: isListening ? '#ff416c' : 'rgba(255,255,255,0.1)', color: 'white', cursor: 'pointer' }}><Mic /></button>
                        <button onClick={() => handleSend()} style={{ width: '50px', borderRadius: '12px', border: 'none', background: 'linear-gradient(to right, #00c6ff, #0072ff)', color: 'white', cursor: 'pointer' }}><Send /></button>
                    </div>
                </div>
                <AnimatePresence>{showAdmin && <AdminDashboard onClose={() => setShowAdmin(false)} />}</AnimatePresence>
            </div>
        </div>
    )
}
