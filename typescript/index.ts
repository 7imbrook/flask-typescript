import {api} from './generated/client/api'

async function main() {
    const number = await api({
        url: '/number',
        custom_id: 15
    })
    console.log(number.id)

    const post = await api({
        url: '/post',
        payload: {
            name: "hello",
            scope: "global"
        }
    })
    console.log(post.size)

    const naming = await api({
        url: '/naming',
        idz: number,
        payload: {
            name: 'test',
            scope: 'local'
        }
    })
    console.log(naming.id)

    const response = await api({
        url: '/via_query',
        custom_id: 123
    })
    console.log(response.name)

}
main()