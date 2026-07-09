const API=process.env.NEXT_PUBLIC_API_URL??'http://localhost:8000/api';
export {API};
export async function api<T>(path:string, init?:RequestInit):Promise<T>{const r=await fetch(`${API}${path}`,{...init,headers:{'Content-Type':'application/json',...(init?.headers||{})}}); if(!r.ok){let m='API-Fehler'; try{m=(await r.json()).detail??m}catch{} throw new Error(m)} return r.json();}
