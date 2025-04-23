import { ethers } from 'ethers'

declare global {
    interface Window {
        ethereum: any; // 型をanyとして定義。必要に応じて詳細な型に変更可能
    }
}

/**
 * getSigner
 * @description ブラウザのウォレットを使用してサインするための関数
 * @returns {Promise<ethers.Signer>} サインするためのSigner
 */
const getSigner = async (): Promise<ethers.Signer> => {
    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    console.log("My Address: ", await signer.getAddress());
    return signer;
}

export default getSigner;
